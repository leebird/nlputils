package edu.delaware.nlp;

import edu.delaware.nlp.BllipParserGrpc.BllipParserBlockingStub;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.StatusRuntimeException;

import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.Map;
import java.util.HashMap;


public class BllipClient {
    private static final Logger logger = Logger.getLogger(BllipClient.class.getName());

    private final ManagedChannel channel;
    private final BllipParserBlockingStub blockingStub;

    /**
     * Construct client for accessing RoutGuide server at host:port.
     */
    public BllipClient(String host, int port) {
        channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext(true)
                .build();
        blockingStub = BllipParserGrpc.newBlockingStub(channel);
    }

    public void shutdown() throws InterruptedException {
        channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
    }

    public Map<String, String> parse(Map<String, String> sentences) {
        RpcProto.BllipParserRequest.Builder rbuilder = RpcProto.BllipParserRequest.newBuilder();
        rbuilder.putAllSentence(sentences);
        RpcProto.BllipParserResponse response;

        try {
            response = blockingStub.parse(rbuilder.build());
            return response.getParse();
        } catch (StatusRuntimeException e) {
            logger.log(Level.WARNING, "RPC failed: {0}", e.getStatus());
            return null;
        }
    }

    public static void main(String[] args) throws InterruptedException {
        BllipClient client = new BllipClient("localhost", 8901);
        try {
            HashMap<String, String> sentences = new HashMap<String, String>();
            sentences.put("test", "I have a book.");
            sentences.put("test2", "This analysis identified activation of known DNA damage response pathways (e.g., phosphorylation of MKK3/6, p38, MK2, Hsp27, p53 and Chk1) as well as of prosurvival (e.g., MEK-ERK, cAMP response element-binding protein (CREB), protein kinase C (PKC)) and antiapoptotic markers (e.g., Bad, Bcl-2).");
            sentences.put("test3", "[miR-126 inhibits colon cancer proliferation and invasion through targeting IRS1, SLC7A5 and TOM1 gene].");
            System.out.println(client.parse(sentences));
        } finally {
            client.shutdown();
        }
    }
}
