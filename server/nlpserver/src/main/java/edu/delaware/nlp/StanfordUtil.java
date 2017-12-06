package edu.delaware.nlp;

import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.semgraph.SemanticGraphEdge;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.CollapsedCCProcessedDependenciesAnnotation;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.BasicDependenciesAnnotation;
import edu.stanford.nlp.trees.TreeCoreAnnotations.TreeAnnotation;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.ling.CoreAnnotations.PartOfSpeechAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.util.CoreMap;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.trees.CollinsHeadFinder;
import edu.stanford.nlp.trees.GrammaticalRelation;
import edu.stanford.nlp.trees.UniversalEnglishGrammaticalRelations;
import edu.stanford.nlp.trees.UniversalEnglishGrammaticalStructure;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.ling.HasOffset;
import edu.stanford.nlp.semgraph.semgrex.SemgrexPattern;
import edu.stanford.nlp.semgraph.semgrex.SemgrexMatcher;
import edu.stanford.nlp.process.Morphology;
import edu.stanford.nlp.trees.TreeLemmatizer;
import edu.stanford.nlp.international.Language;

//import java.util.*;
import java.util.List;
import java.util.Set;
import java.util.LinkedList;
import java.util.Map;
import java.util.HashMap;
import java.util.TreeSet;
import java.util.Collection;
import java.util.Queue;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;


public class StanfordUtil {
    private static final Logger logger = Logger.getLogger(StanfordUtil.class.getName());
    private final String parseAnnotators;
    private final String splitAnnotators;
    private final int maxParseSeconds;
    private StanfordCoreNLP parsePipeline;
    private StanfordCoreNLP splitPipeline;
    private CollinsHeadFinder headFinder;

    public StanfordUtil(int maxParseSeconds) {
        this.parseAnnotators = "tokenize, ssplit, pos, lemma, parse";
        this.splitAnnotators = "tokenize, ssplit, pos, lemma";
        this.maxParseSeconds = maxParseSeconds;
        loadPipeline();
    }

    //    public StanfordUtil(String annotators) {
    //        this.annotators = annotators;
    //        this.maxParseSeconds = 0;
    //        loadPipeline();
    //    }

    private void loadPipeline() {
        // Initialize StanfordNLP pipeline.
        // creates a StanfordCoreNLP object, with POS tagging, lemmatization, NER, parsing, and coreference resolution
        Properties props = new Properties();
        // 300 seconds for the whole parsing process for a document.
        if (maxParseSeconds > 0) {
            props.setProperty("parse.maxtime", Integer.toString(maxParseSeconds * 1000));
        }
        props.setProperty("annotators", parseAnnotators);
        props.setProperty("parse.originalDependencies", "true");
        parsePipeline = new StanfordCoreNLP(props);

        props = new Properties();
        props.setProperty("annotators", splitAnnotators);
        splitPipeline = new StanfordCoreNLP(props);

        headFinder = new CollinsHeadFinder();
    }

    public Map<String, String> splitSentence(String text) {
        // create an empty Annotation just with the given text
        Annotation document = new Annotation(text);
        // run all Annotators on this text
        splitPipeline.annotate(document);

        // these are all the sentences in this document
        // a CoreMap is essentially a Map that uses class objects as keys and has values with custom types
        List<CoreMap> sentences = document.get(SentencesAnnotation.class);

        int sentIndex = 0;
        HashMap<String, String> sentence_map = new HashMap<String, String>();
        for (CoreMap sentence : sentences) {
            sentence_map.put(Integer.toString(sentIndex), sentence.toString());
            sentIndex++;
        }
        return sentence_map;
    }
    
    public DocumentProto.Document parseUsingBllip(DocumentProto.Document protoDoc,
						  Map<String, String> sentences,
						  Map<String, String> parses ) {
        String text = protoDoc.getText();
        DocumentProto.Document.Builder dbuilder = protoDoc.toBuilder();
    
        TreeLemmatizer treeLemmatizer = new TreeLemmatizer();

        int tokenIndex = 0;
        int sentIndex = 0;
        int charIndex = 0;

        for (int i = 0; i < sentences.size(); i++) {
            // We use sentence order as sentence id.
            String sentence_id = Integer.toString(i);
            String sentence_text = sentences.get(sentence_id);
            String parse = parses.get(sentence_id);
            // Starting character offset of current sentence. Search from the last
	    // offset of charIndex.
            charIndex = text.indexOf(sentence_text, charIndex);

            if (parse == null) {
                // We skip sentences with no parse, but the necessary index
                // will be updated properly, except tokenIndex, sentIndex will
                // skip the current sentence. Seems OK but may need to find a
                // better way to handle the missing parses.
                logger.warning("Sentence parse error: " + protoDoc.getDocId() + ", sentence " + i);
                continue;
            }

            // this is the parse tree of the current sentence
            // obtained from Charniak Bllip parser.
            Tree tree = Tree.valueOf(parse);
            // Lemmatize the tree from BLLIP parser.
            tree = treeLemmatizer.transformTree(tree);
            List<Tree> leaves = tree.getLeaves();

            // traversing the words in the current sentence
            // a CoreLabel is a CoreMap with additional token-specific methods
            int sentenceBoundary = -1;
            int sentenceTokenIndex = 1;
            HashMap<Integer, Integer> indexMap = new HashMap<Integer, Integer>();
            DocumentProto.Sentence.Builder sbuilder = DocumentProto.Sentence.newBuilder();

            // Save the parse in penn tree bank format.
            sbuilder.setParse(parse);
	    sbuilder.setCharStart(charIndex);
	    sbuilder.setCharEnd(charIndex + sentence_text.length() - 1);

            for (Tree leaf : leaves) {
                if (sentenceBoundary == -1) {
                    sbuilder.setTokenStart(tokenIndex);
                }

                Tree preTerminal = leaf.parent(tree);

                HasOffset leafLabel = (HasOffset) leaf.label();
                HasOffset preTerminalLabel = (HasOffset) preTerminal.label();

                String word = leaf.label().value();
                String pos = preTerminal.label().value();
                String unescaped = BllipUtil.unescape(word);
                String lemma = ((HasLemma) leaf.label()).lemma();
                int wordCharStart = text.indexOf(unescaped, charIndex);

                assert wordCharStart >= 0 : sentence_text;

                int wordCharEnd = wordCharStart + unescaped.length() - 1;
                charIndex = wordCharEnd + 1;

                // Note that if any of the field is the default value, it woun't be printed.
                // For example, if the first token is "I", the its char_start, char_end and
                // token_id won't be printed by TextFormat.printToString().
                DocumentProto.Token.Builder tbuilder = DocumentProto.Token.newBuilder();
                tbuilder.setWord(unescaped);
                tbuilder.setPos(pos);
                // Add lemma for bllip parser token.
                // tbuilder.setLemma(morph.lemma(unescaped, pos));
                tbuilder.setLemma(lemma);
                // tbuilder.setLemma(token.lemma());
                tbuilder.setCharStart(wordCharStart);
                tbuilder.setCharEnd(wordCharEnd);

                // Set the token offset as it is not set by reading the penn tree
                // bank parse tree produced by Bllip parser.
                // Here we add 1 to the end offsets to be consistent with the
                // Stanford parser output. In Stanford parser, the end offset is the
                // position of the last character + 1. Doing so we can use one
                // buildConstituent() function to build constituents for both Stanford
                // and Bllip outputs.
                leafLabel.setBeginPosition(wordCharStart);
                leafLabel.setEndPosition(wordCharEnd + 1);
                preTerminalLabel.setBeginPosition(wordCharStart);
                preTerminalLabel.setEndPosition(wordCharEnd + 1);

                tbuilder.setIndex(tokenIndex);
                dbuilder.addToken(tbuilder);
                indexMap.put(sentenceTokenIndex, tokenIndex);
                sentenceBoundary = tokenIndex;
                sentenceTokenIndex++;
                tokenIndex++;
            }
            sbuilder.setTokenEnd(tokenIndex - 1);
            sbuilder.setIndex(sentIndex);
            sentIndex++;


            buildConstituent(sbuilder, tree, indexMap);

            // this is the Stanford dependency graph of the current sentence
            // Generated from Billip parser.
            UniversalEnglishGrammaticalStructure sd = new UniversalEnglishGrammaticalStructure(tree);
	    // Here is the problem, advcl:compared_to changed to advcl only in 3.8.
	    // https://github.com/stanfordnlp/CoreNLP/blob/master/src/edu/stanford/nlp/trees/UniversalEnglishGrammaticalStructure.java
	    // search for compared_to
	    // System.out.println(sd.typedDependenciesCCprocessed());
            SemanticGraph dependencies = new SemanticGraph(sd.typedDependenciesCCprocessed());
                
            buildDependency(sbuilder, dependencies, indexMap);

            dbuilder.addSentence(sbuilder);
        }
        return dbuilder.build();
    }

    public DocumentProto.Document parseUsingBllipEDG(DocumentProto.Document protoDoc,
						     Map<String, String> sentences,
						     Map<String, String> parses,
						     EdgRulesProto.EdgRules protoRules) {
        String text = protoDoc.getText();
	List<EdgRulesProto.Rule> rules = protoRules.getRulesList();
        //List<DocumentProto.Rule> rules = protoDoc.getRulesList();
    
        DocumentProto.Document.Builder dbuilder = protoDoc.toBuilder();
    
        TreeLemmatizer treeLemmatizer = new TreeLemmatizer();

        int tokenIndex = 0;
        int sentIndex = 0;
        int charIndex = 0;

	HashMap<Integer, String> charEntityMap = new HashMap<Integer, String>();
	for (Map.Entry<String, DocumentProto.Entity> entry : protoDoc.getEntityMap().entrySet()) {
	    DocumentProto.Entity entity = entry.getValue();
	    for (int i = entity.getCharStart(); i <= entity.getCharEnd(); i++) {
		String prev = (charEntityMap.get(i) == null) ? "" : charEntityMap.get(i);
		// <PROTEIN><PROTEIN_PART>
		charEntityMap.put(i, prev+"<"+entity.getEntityType()+">");
	    }
	}

        for (int i = 0; i < sentences.size(); i++) {
            // We use sentence order as sentence id.
            String sentence_id = Integer.toString(i);
            String sentence_text = sentences.get(sentence_id);
            String parse = parses.get(sentence_id);
            // Starting character offset of current sentence.
            charIndex = text.indexOf(sentence_text, charIndex);
            // Starting point for next search.
            // charIndex += sentence_text.length();

            if (parse == null) {
                // We skip sentences with no parse, but the necessary index
                // will be updated properly, except tokenIndex, sentIndex will
                // skip the current sentence. Seems OK but may need to find a
                // better way to handle the missing parses.
                logger.warning("Sentence parse error: " + protoDoc.getDocId() + ", sentence " + i);
                continue;
            }

            // this is the parse tree of the current sentence
            // obtained from Charniak Bllip parser.
            Tree tree = Tree.valueOf(parse);
            // Lemmatize the tree from BLLIP parser.
            tree = treeLemmatizer.transformTree(tree);
            List<Tree> leaves = tree.getLeaves();

            // traversing the words in the current sentence
            // a CoreLabel is a CoreMap with additional token-specific methods
            int sentenceBoundary = -1;
            int sentenceTokenIndex = 1;
            HashMap<Integer, Integer> indexMap = new HashMap<Integer, Integer>();
            DocumentProto.Sentence.Builder sbuilder = DocumentProto.Sentence.newBuilder();

            // Save the parse in penn tree bank format.
            sbuilder.setParse(parse);
	    sbuilder.setCharStart(charIndex);
	    sbuilder.setCharEnd(charIndex + sentence_text.length() - 1);

            for (Tree leaf : leaves) {
                if (sentenceBoundary == -1) {
                    sbuilder.setTokenStart(tokenIndex);
                }

                Tree preTerminal = leaf.parent(tree);

                HasOffset leafLabel = (HasOffset) leaf.label();
                HasOffset preTerminalLabel = (HasOffset) preTerminal.label();

                String word = leaf.label().value();
                String pos = preTerminal.label().value();
                String unescaped = BllipUtil.unescape(word);
                String lemma = ((HasLemma) leaf.label()).lemma();
                int wordCharStart = text.indexOf(unescaped, charIndex);

                assert wordCharStart >= 0 : sentence_text;

                int wordCharEnd = wordCharStart + unescaped.length() - 1;
                charIndex = wordCharEnd + 1;

                // Note that if any of the field is the default value, it woun't be printed.
                // For example, if the first token is "I", the its char_start, char_end and
                // token_id won't be printed by TextFormat.printToString().
                DocumentProto.Token.Builder tbuilder = DocumentProto.Token.newBuilder();
                tbuilder.setWord(unescaped);
                tbuilder.setPos(pos);
                // Add lemma for bllip parser token.
                // tbuilder.setLemma(morph.lemma(unescaped, pos));
                tbuilder.setLemma(lemma);
                // tbuilder.setLemma(token.lemma());
                tbuilder.setCharStart(wordCharStart);
                tbuilder.setCharEnd(wordCharEnd);

                // Set the token offset as it is not set by reading the penn tree
                // bank parse tree produced by Bllip parser.
                // Here we add 1 to the end offsets to be consistent with the
                // Stanford parser output. In Stanford parser, the end offset is the
                // position of the last character + 1. Doing so we can use one
                // buildConstituent() function to build constituents for both Stanford
                // and Bllip outputs.
                leafLabel.setBeginPosition(wordCharStart);
                leafLabel.setEndPosition(wordCharEnd + 1);
                preTerminalLabel.setBeginPosition(wordCharStart);
                preTerminalLabel.setEndPosition(wordCharEnd + 1);

                tbuilder.setIndex(tokenIndex);
                dbuilder.addToken(tbuilder);
                indexMap.put(sentenceTokenIndex, tokenIndex);
                sentenceBoundary = tokenIndex;
                sentenceTokenIndex++;
                tokenIndex++;
            }
            sbuilder.setTokenEnd(tokenIndex - 1);
            sbuilder.setIndex(sentIndex);
            sentIndex++;

            buildConstituent(sbuilder, tree, indexMap);

            // this is the Stanford dependency graph of the current sentence
            // Generated from Billip parser.
            UniversalEnglishGrammaticalStructure sd = new UniversalEnglishGrammaticalStructure(tree);
            SemanticGraph dependencies = new SemanticGraph(sd.typedDependenciesCCprocessed());

	    // Set entity type for all tokens.
	    for(IndexedWord word : dependencies.vertexSet()) {
		String start_type = charEntityMap.get(word.beginPosition());
		String end_type = charEntityMap.get(word.endPosition()-1);
		start_type = start_type == null ? "" : start_type;
		end_type = end_type == null ? "" : end_type;
		String curr_type = word.ner() == null ? "" : word.ner();
		
		// Sometimes start_type and end_type are different, we use the longest one.
		// N-glycan: CHEMICAL, glycan: SUGAR
		if (start_type.length() > curr_type.length())
		    word.setNER(start_type);
		if (end_type.length() > curr_type.length())
		    word.setNER(end_type);
	    }

	    //String depString = dependencies.toFormattedString();

            //Semregex Matching done : Samir
            for(EdgRulesProto.Rule rule : rules) {
                String ruleID = rule.getIdent(); 
		String ruleRegex = rule.getRegex();
                List <EdgRulesProto.Action> actions = rule.getActionsList();
                SemgrexPattern pat = SemgrexPattern.compile(ruleRegex);
                SemgrexMatcher mat = pat.matcher(dependencies);
                buildExtraDependency(sbuilder, mat, actions, ruleID, indexMap, dependencies);
            }

            buildDependency(sbuilder, dependencies, indexMap);

            dbuilder.addSentence(sbuilder);
        }
        return dbuilder.build();
    }

    public DocumentProto.Document parseUsingStanford(DocumentProto.Document protoDoc) {
        String text = protoDoc.getText();
        DocumentProto.Document.Builder dbuilder = protoDoc.toBuilder();

        // create an empty Annotation just with the given text
        Annotation document = new Annotation(text);

        // run all Annotators on this text
        parsePipeline.annotate(document);

        // these are all the sentences in this document
        // a CoreMap is essentially a Map that uses class objects as keys and has values with custom types
        List<CoreMap> sentences = document.get(SentencesAnnotation.class);

        int tokenIndex = 0;
        int sentIndex = 0;
        for (CoreMap sentence : sentences) {
            // traversing the words in the current sentence
            // a CoreLabel is a CoreMap with additional token-specific methods
            int sentenceBoundary = -1;
	    int charEnd = 0;
            HashMap<Integer, Integer> indexMap = new HashMap<Integer, Integer>();
            DocumentProto.Sentence.Builder sbuilder = DocumentProto.Sentence.newBuilder();

            for (CoreLabel token : sentence.get(TokensAnnotation.class)) {
                if (sentenceBoundary == -1) {
                    sbuilder.setTokenStart(tokenIndex);
		    sbuilder.setCharStart(token.beginPosition());
                }
                // this is the POS tag of the token
                String pos = token.get(PartOfSpeechAnnotation.class);
		
		charEnd = token.endPosition() - 1;
		
                // Note that if any of the field is the default value, it woun't be printed.
                // For example, if the first token is "I", the its char_start, char_end and
                // token_id won't be printed by TextFormat.printToString().
                DocumentProto.Token.Builder tbuilder = DocumentProto.Token.newBuilder();
                tbuilder.setWord(token.originalText());
                tbuilder.setPos(pos);
                tbuilder.setLemma(token.lemma());
                tbuilder.setCharStart(token.beginPosition());
                // token.endPosition() is the position after the last character.
                tbuilder.setCharEnd(token.endPosition() - 1);
                tbuilder.setIndex(tokenIndex);
                dbuilder.addToken(tbuilder);
                indexMap.put(token.index(), tokenIndex);
                sentenceBoundary = tokenIndex;
                tokenIndex++;
            }

            sbuilder.setTokenEnd(tokenIndex - 1);
	    sbuilder.setCharEnd(charEnd);
            sbuilder.setIndex(sentIndex);
            sentIndex++;

            // this is the parse tree of the current sentence
            Tree tree = sentence.get(TreeAnnotation.class);
            buildConstituent(sbuilder, tree, indexMap);

            // this is the Stanford dependency graph of the current sentence
            SemanticGraph dependencies = sentence.get(CollapsedCCProcessedDependenciesAnnotation.class);
            buildDependency(sbuilder, dependencies, indexMap);
            dbuilder.addSentence(sbuilder);
        }

        return dbuilder.build();
    }

    public DocumentProto.Document splitSentence(DocumentProto.Document protoDoc) {
        String text = protoDoc.getText();
        DocumentProto.Document.Builder dbuilder = protoDoc.toBuilder();

        // create an empty Annotation just with the given text
        Annotation document = new Annotation(text);

        // run all Annotators on this text
        splitPipeline.annotate(document);

        // these are all the sentences in this document
        // a CoreMap is essentially a Map that uses class objects as keys and has values with custom types
        List<CoreMap> sentences = document.get(SentencesAnnotation.class);

        int tokenIndex = 0;
        int sentIndex = 0;
        for (CoreMap sentence : sentences) {
            // traversing the words in the current sentence
            // a CoreLabel is a CoreMap with additional token-specific methods
            int sentenceBoundary = -1;
            int charEnd = 0;

            DocumentProto.Sentence.Builder sbuilder = DocumentProto.Sentence.newBuilder();

            for (CoreLabel token : sentence.get(TokensAnnotation.class)) {
                if (sentenceBoundary == -1) {
                    sbuilder.setTokenStart(tokenIndex);
		    sbuilder.setCharStart(token.beginPosition());
                }
                String pos = token.get(PartOfSpeechAnnotation.class);
		charEnd = token.endPosition() - 1;
                // Note that if any of the field is the default value, it won't be printed.
                // For example, if the first token is "I", the its char_start, char_end and
                // token_id won't be printed by TextFormat.printToString().
                DocumentProto.Token.Builder tbuilder = DocumentProto.Token.newBuilder();
                tbuilder.setWord(token.originalText());
                tbuilder.setLemma(token.lemma());
                tbuilder.setPos(pos);
                tbuilder.setCharStart(token.beginPosition());
                // token.endPosition() is the position after the last character.
                tbuilder.setCharEnd(token.endPosition() - 1);
                tbuilder.setIndex(tokenIndex);
                dbuilder.addToken(tbuilder);
                // indexMap.put(token.index(), tokenIndex);
                sentenceBoundary = tokenIndex;
                tokenIndex++;
            }
	    
            sbuilder.setTokenEnd(tokenIndex - 1);
	    sbuilder.setCharEnd(charEnd);
            sbuilder.setIndex(sentIndex);
            dbuilder.addSentence(sbuilder);

            sentIndex++;

        }
        // dbuilder.clearText();
        return dbuilder.build();
    }

    private void buildExtraDependency(DocumentProto.Sentence.Builder sbuilder,
                                      SemgrexMatcher mat,
                                      List <EdgRulesProto.Action> actions,
                                      String ruleID,
                                      HashMap<Integer, Integer> indexMap,
                                      SemanticGraph dependencies) {

        LinkedList<SemanticGraphEdge> newEdges = new LinkedList<SemanticGraphEdge>();
        while (mat.find()) {
	    ///////////////////////////////////////
	    Set<String> matchedNodeNames = mat.getNodeNames();
	    Set<String> relNames = mat.getRelationNames();

            for (EdgRulesProto.Action action : actions) {
                String govNodeName = action.getGovNode();
                String depNodeName = action.getDepNode();
                String edgeLabel = action.getEdgeLabel();

		//Adding Functionality to name relations
		//and replace it in edge labels of actions
		for (String relName : relNames) {
		    String relEdgeStr = mat.getRelnString(relName);
		    if(edgeLabel.contains(relName)) {
			String newEdgeLabel = edgeLabel.replaceFirst(relName,relEdgeStr);
			edgeLabel = newEdgeLabel;
		    }
		}
		/////////////////////////////////////////
                int addDep = 0; //if both action node name found adddDep >=2
                for(String matchNodeName : matchedNodeNames) {
                    if(govNodeName.equals(matchNodeName)) { addDep = addDep +1;}
                    if(depNodeName.equals(matchNodeName)) { addDep = addDep +1;}
                }
                if (addDep >= 2) {
                    IndexedWord govNode = mat.getNode(govNodeName);
                    IndexedWord depNode = mat.getNode(depNodeName);
                    int depIndex = indexMap.get(depNode.index());
                    int govIndex = indexMap.get(govNode.index());
                    DocumentProto.Sentence.DependencyExtra.Builder depExBuilder = DocumentProto.Sentence.DependencyExtra.newBuilder();
                    depExBuilder.setDepIndex(depIndex);
                    depExBuilder.setGovIndex(govIndex);
                    depExBuilder.setRelation(edgeLabel);
                    depExBuilder.setRuleId(ruleID);

                    //Store the new edges to a list
                    SemanticGraphEdge newEdge = new SemanticGraphEdge(govNode,depNode,GrammaticalRelation.valueOf(Language.English,edgeLabel ), Double.NEGATIVE_INFINITY, false);
                    newEdges.add(newEdge);    
                    //Changing the dependencies in while(mat.find()) sometimes throws an exception
                    //dependencies.addEdge(govNode,depNode,GrammaticalRelation.valueOf(Language.English,edgeLabel ), Double.NEGATIVE_INFINITY, false);
                    
                    sbuilder.addDependencyExtra(depExBuilder);
		    // System.out.println(ruleID + ": " + govNode.toString() + ">" + edgeLabel + ">" + depNode.toString());
                }
            }    
        }
        //After the rules have been applied add the new edges to the semantic graph (old one)
        for(SemanticGraphEdge newEdge: newEdges) {
	    // Only add non-existing edges.
	    // SemanticGraph.containsEdge() only checks two vertices but not relation.
	    // Use getEdge() instead.
	    if (dependencies.getEdge(newEdge.getGovernor(), newEdge.getDependent(), newEdge.getRelation()) == null)
		dependencies.addEdge(newEdge);
        }
    }

    private void buildDependency(DocumentProto.Sentence.Builder sbuilder,
                                 SemanticGraph dependencies,
                                 HashMap<Integer, Integer> indexMap) {
        // Add root relations. The root links to itself with the relation "root".
        Collection<IndexedWord> roots = dependencies.getRoots();
        for (IndexedWord root : roots) {
            int rootIndex = indexMap.get(root.index());
            DocumentProto.Sentence.Dependency.Builder depBuilder = DocumentProto.Sentence.Dependency.newBuilder();
            depBuilder.setDepIndex(rootIndex);
            depBuilder.setGovIndex(rootIndex);
            depBuilder.setRelation("root");
            sbuilder.addDependency(depBuilder);
        }

        // This only gets basic dependencies.
        // Collection<TypedDependency> typedDeps = dependencies.typedDependencies();
        // for (TypedDependency typedDep : typedDeps) {

        // Correct way to get collapsed and ccprocessed relations.
        for (SemanticGraphEdge edge : dependencies.edgeIterable()) {
            IndexedWord gov = edge.getGovernor();
            IndexedWord dep = edge.getDependent();

            int depIndex = indexMap.get(dep.index());
            int govIndex = indexMap.get(gov.index());

            // Only toString can get the collapsed and ccprocessed relations.
            // Neither getShortName() and getLongName() can. Don't know why.
            String depTag = edge.getRelation().toString();
	    //String depTag = edge.getRelation().getShortName();
	    //System.out.println(edge.getRelation().getShortName() + " " + edge.getRelation().getLongName() + " "+ edge.getRelation().toString() + " "+ edge.getRelation().getSpecific());
            DocumentProto.Sentence.Dependency.Builder depBuilder = DocumentProto.Sentence.Dependency.newBuilder();
            depBuilder.setDepIndex(depIndex);
            depBuilder.setGovIndex(govIndex);
            depBuilder.setRelation(depTag);
            sbuilder.addDependency(depBuilder);

        }
    }

    private void buildConstituent(DocumentProto.Sentence.Builder sbuilder,
                                  Tree tree,
                                  HashMap<Integer, Integer> indexMap) {
        Tree nextTree = tree;
        Queue<Tree> treeQueue = new LinkedList<Tree>();
        Queue<Integer> parentQueue = new LinkedList<Integer>();
        int treeIndex = 0;
        parentQueue.add(0);
        while (nextTree != null) {
            int parentIndex = parentQueue.poll();
            // Get the head leaf.
            Tree head = nextTree.headTerminal(headFinder);
            List<Tree> headLeaves = head.getLeaves();
            assert headLeaves.size() == 1;
            Tree onlyLeaf = headLeaves.get(0);
            CoreLabel headToken = (CoreLabel) onlyLeaf.label();

            // Get char start and end for the head token.
            int headStart = ((HasOffset) onlyLeaf.label()).beginPosition();
            // It looks the end position is the last char index + 1.
            int headEnd = ((HasOffset) onlyLeaf.label()).endPosition() - 1;
            // Get head token index.
            int headIndex = indexMap.get(headToken.index());

            // Get char start and end for the phrase.
            List<Tree> treeLeaves = nextTree.getLeaves();
            Tree firstLeaf = treeLeaves.get(0);
            Tree lastLeaf = treeLeaves.get(treeLeaves.size() - 1);
            int phraseStart = ((HasOffset) firstLeaf.label()).beginPosition();
            // It looks the end position is the last char index + 1.
            int phraseEnd = ((HasOffset) lastLeaf.label()).endPosition() - 1;

            CoreLabel firstToken = (CoreLabel) firstLeaf.label();
            CoreLabel lastToken = (CoreLabel) lastLeaf.label();

            int firstTokenIndex = indexMap.get(firstToken.index());
            int lastTokenIndex = indexMap.get(lastToken.index());

            assert phraseEnd >= phraseStart;
            assert phraseStart >= 0;

            DocumentProto.Sentence.Constituent.Builder cbuilder = DocumentProto.Sentence.Constituent.newBuilder();
            cbuilder.setLabel(nextTree.label().value());

            // Don't use character offset.
            // cbuilder.setCharStart(phrase_start);
            // cbuilder.setCharEnd(phrase_end);
            // cbuilder.setHeadCharStart(head_start);
            // cbuilder.setHeadCharEnd(head_end);

            cbuilder.setTokenStart(firstTokenIndex);
            cbuilder.setTokenEnd(lastTokenIndex);
            cbuilder.setHeadTokenIndex(headIndex);

            cbuilder.setIndex(treeIndex);
            cbuilder.setParent(parentIndex);
            // Add children index to its parent.
            if (parentIndex < treeIndex) {
                sbuilder.getConstituentBuilder(parentIndex).addChildren(treeIndex);
            }
            for (Tree child : nextTree.children()) {
                treeQueue.add(child);
                parentQueue.add(treeIndex);
            }
            sbuilder.addConstituent(cbuilder);
            treeIndex++;
            nextTree = treeQueue.poll();
        }
    }
}
