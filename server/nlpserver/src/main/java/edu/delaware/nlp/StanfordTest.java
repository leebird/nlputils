package edu.delaware.nlp;

import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.IndexedWord;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.semgraph.SemanticGraphEdge;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.CollapsedCCProcessedDependenciesAnnotation;
import edu.stanford.nlp.util.CoreMap;

import java.util.*;

// The codes below are largely based on http://www.grpc.io/docs/tutorials/basic/java.html.

public class StanfordTest {
    private StanfordCoreNLP pipeline;

    public StanfordTest() {
        // Initialize StanfordNLP pipeline.
        // creates a StanfordCoreNLP object, with POS tagging, lemmatization, NER, parsing, and coreference resolution
        Properties props = new Properties();
	// props.setProperty("depparse.extradependencies", "SUBJ_ONLY");
        props.setProperty("annotators", "tokenize, ssplit, pos, lemma, ner, parse, dcoref");

        //props.setProperty("annotators", "tokenize, ssplit");
        pipeline = new StanfordCoreNLP(props);
    }

    public static void main(String[] args) {
        StanfordTest s = new StanfordTest();
        // create an empty Annotation just with the given text
        // It seems stanford parser doesn't split on slash '/'
        // See http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.216.2433&rep=rep1&type=pdf
        Annotation document = new Annotation("The genes encoding the functionally related hepatocyte nuclear factors HNF-1alpha and HNF-4alpha play a critical role in normal pancreatic beta-cell function.");

        // run all Annotators on this text
        s.pipeline.annotate(document);

        for (CoreMap sentence : document.get(SentencesAnnotation.class)) {
            for (CoreLabel token : sentence.get(TokensAnnotation.class)) {
                System.out.println(token.originalText());
            }

            SemanticGraph dependencies = sentence.get(CollapsedCCProcessedDependenciesAnnotation.class);
	    System.out.println(dependencies.toString());
            // Correct way to get collapsed and ccprocessed relations.
            for (SemanticGraphEdge edge : dependencies.edgeIterable()) {
                IndexedWord gov = edge.getGovernor();
                IndexedWord dep = edge.getDependent();

                // Only toString can get the collapsed and ccprocessed relations.
                // Neither getShortName() and getLongName() can. Don't know why.
                String depTag = edge.getRelation().toString();
                System.out.println(depTag + " " + gov.toString() + " " + dep.toString());
                // String depTag = edge.getRelation().getShortName();

            }
        }
    }
}


