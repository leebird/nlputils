import edu.delaware.nlp.NlpServiceGrpc;
import edu.delaware.nlp.Protobuf;
import edu.stanford.nlp.ling.CoreAnnotations.PartOfSpeechAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.IndexedWord;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.CollapsedCCProcessedDependenciesAnnotation;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreeCoreAnnotations.TreeAnnotation;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.util.CoreMap;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;

import java.io.IOException;
import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;

// The codes below are largely based on http://www.grpc.io/docs/tutorials/basic/java.html.

public class StanfordLocal {
    private StanfordCoreNLP pipeline;

    public StanfordLocal() {
        // Initialize StanfordNLP pipeline.
        // creates a StanfordCoreNLP object, with POS tagging, lemmatization, NER, parsing, and coreference resolution
        Properties props = new Properties();
        // props.setProperty("annotators", "tokenize, ssplit, pos, lemma, ner, parse, dcoref");
        props.setProperty("annotators", "tokenize, ssplit, pos, lemma, parse");
        pipeline = new StanfordCoreNLP(props);
    }

    public static void main(String[] args) {
        StanfordLocal s = new StanfordLocal();
        Protobuf.Document.Builder dbuilder = Protobuf.Document.newBuilder();
        for (int i = 0; i < 1000; i++) {
//            dbuilder.setText("The alpha subunit of skeletal muscle phosphorylase kinase, as isolated, carries phosphate at the serine residues 1018, 1020 and 1023. Employing the S-ethyl-cysteine method, these residues are found to be phosphorylated partially, i.e. differently phosphorylated species exist in muscle. Serine 1018 is a site which can be phosphorylated by the cyclic-AMP-dependent protein kinase. The serine residues 972, 985 and 1007 are phosphorylated by phosphorylase kinase itself when its activity is stimulated by micromolar concentrations of Ca2+. These phosphorylation sites are not identical to those found to be phosphorylated already in the enzyme as prepared from freshly excised muscle. A 'multiphosphorylation loop' uniquely present in this but not in the homologous beta subunit contains all the phosphoserine residues so far identified in the alpha subunit.");
//            s.annotate(dbuilder.build());
            s.annotate("The alpha subunit of skeletal muscle phosphorylase kinase, as isolated, carries phosphate at the serine residues 1018, 1020 and 1023. Employing the S-ethyl-cysteine method, these residues are found to be phosphorylated partially, i.e. differently phosphorylated species exist in muscle. Serine 1018 is a site which can be phosphorylated by the cyclic-AMP-dependent protein kinase. The serine residues 972, 985 and 1007 are phosphorylated by phosphorylase kinase itself when its activity is stimulated by micromolar concentrations of Ca2+. These phosphorylation sites are not identical to those found to be phosphorylated already in the enzyme as prepared from freshly excised muscle. A 'multiphosphorylation loop' uniquely present in this but not in the homologous beta subunit contains all the phosphoserine residues so far identified in the alpha subunit.");
            System.out.println(i);
        }
    }

    private Protobuf.Document annotate(Protobuf.Document protoDoc) {
        String text = protoDoc.getText();
        Protobuf.Document.Builder dbuilder = protoDoc.toBuilder();

        // create an empty Annotation just with the given text
        Annotation document = new Annotation(text);

        // run all Annotators on this text
        pipeline.annotate(document);

        // these are all the sentences in this document
        // a CoreMap is essentially a Map that uses class objects as keys and has values with custom types
        List<CoreMap> sentences = document.get(SentencesAnnotation.class);

        int tokenIndex = 0;
        for (
                CoreMap sentence
                : sentences)

        {
            // traversing the words in the current sentence
            // a CoreLabel is a CoreMap with additional token-specific methods
            int sentenceBoundary = -1;
            HashMap<Integer, Integer> indexMap = new HashMap<Integer, Integer>();
            for (CoreLabel token : sentence.get(TokensAnnotation.class)) {

                // this is the POS tag of the token
                String pos = token.get(PartOfSpeechAnnotation.class);

                // Note that if any of the field is the default value, it woun't be printed.
                // For example, if the first token is "I", the its char_start, char_end and
                // token_id won't be printed by TextFormat.printToString().
                Protobuf.Token.Builder tbuilder = Protobuf.Token.newBuilder();
                tbuilder.setWord(token.originalText());
                tbuilder.setPos(pos);
                tbuilder.setCharStart(token.beginPosition());
                // token.endPosition() is the position after the last character.
                tbuilder.setCharEnd(token.endPosition() - 1);
                tbuilder.setTokenId(tokenIndex);
                dbuilder.addToken(tbuilder);
                indexMap.put(token.index(), tokenIndex);
                sentenceBoundary = tokenIndex;
                tokenIndex++;
            }

            Protobuf.Document.Boundary.Builder bbuilder = Protobuf.Document.Boundary.newBuilder();
            bbuilder.setLevel(Protobuf.Document.Boundary.Level.SENTENCE);
            bbuilder.setTokenIndex(sentenceBoundary);
            dbuilder.addBoundary(bbuilder);

            // this is the parse tree of the current sentence
            Tree tree = sentence.get(TreeAnnotation.class);

            // this is the Stanford dependency graph of the current sentence
            SemanticGraph dependencies = sentence.get(CollapsedCCProcessedDependenciesAnnotation.class);

            HashMap<Integer, TreeSet<Integer>> childrenMap = new HashMap<Integer, TreeSet<Integer>>();
            Collection<TypedDependency> typedDeps = dependencies.typedDependencies();
            for (TypedDependency typedDep : typedDeps) {
                IndexedWord gov = typedDep.gov();
                IndexedWord dep = typedDep.dep();

                int depIndex = indexMap.get(dep.index());
                // Set govIndex to depIndex if dep is the root token.
                int govIndex = depIndex;
                if (gov.index() > 0) {
                    govIndex = indexMap.get(gov.index());
                }

                if (govIndex != depIndex) {
                    if (!childrenMap.containsKey(govIndex)) {
                        childrenMap.put(govIndex, new TreeSet<Integer>());
                    }
                    childrenMap.get(govIndex).add(depIndex);
                }

                String depTag = typedDep.reln().getShortName();

                Protobuf.Token.Builder token = dbuilder.getTokenBuilder(depIndex);
                // The token shouldn't have dependency tag at this point.
                assert token.getDependency().length() == 0;
                // Set the dependency tag.
                token.setDependency(depTag);
                token.setHead(govIndex);
                dbuilder.setToken(depIndex, token);
            }

            for (HashMap.Entry<Integer, TreeSet<Integer>> entry : childrenMap.entrySet()) {
                int govIndex = entry.getKey();
                TreeSet<Integer> children = entry.getValue();
                Protobuf.Token.Builder token = dbuilder.getTokenBuilder(govIndex);
                // At this point, the token shouldn't have children.
                assert token.getChildrenCount() == 0;
                // TreeSet already sorts the children from small to large.
                token.addAllChildren(children);
                dbuilder.setToken(govIndex, token);
            }
        }

        // This is the coreference link graph
        // Each chain stores a set of mentions that link to each other,
        // along with a method for getting the most representative mention
        // Both sentence and token offsets start at 1!
        //        Map<Integer, CorefChain> graph =
        //                document.get(CorefChainAnnotation.class);

//            System.out.println(TextFormat.printToString(dbuilder.build()));
        return dbuilder.build();
    }

    private void annotate(String text) {

        // create an empty Annotation just with the given text
        Annotation document = new Annotation(text);

        // run all Annotators on this text
        pipeline.annotate(document);

        // these are all the sentences in this document
        // a CoreMap is essentially a Map that uses class objects as keys and has values with custom types
        List<CoreMap> sentences = document.get(SentencesAnnotation.class);

        for (CoreMap sentence : sentences)  {
            // this is the parse tree of the current sentence
            Tree tree = sentence.get(TreeAnnotation.class);

            // this is the Stanford dependency graph of the current sentence
            SemanticGraph dependencies = sentence.get(CollapsedCCProcessedDependenciesAnnotation.class);
        }


        // This is the coreference link graph
        // Each chain stores a set of mentions that link to each other,
        // along with a method for getting the most representative mention
        // Both sentence and token offsets start at 1!
        //        Map<Integer, CorefChain> graph =
        //                document.get(CorefChainAnnotation.class);

    }
}
