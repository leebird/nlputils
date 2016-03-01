package edu.delaware.nlp;

import edu.delaware.nlp.DocumentProto;
import edu.delaware.nlp.RpcProto;
import edu.delaware.nlp.NlpServiceGrpc;
import edu.delaware.nlp.BllipParserGrpc;
import edu.delaware.nlp.BllipParserGrpc.BllipParserBlockingStub;
import edu.delaware.nlp.BllipUtil;
import edu.delaware.nlp.StanfordUtil;

import io.grpc.netty.NettyServerBuilder;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.Status;
import io.grpc.StatusRuntimeException;
import io.grpc.stub.StreamObserver;

//import java.util.*;
import java.io.IOException;
import java.util.Iterator;
import java.util.List;
import java.util.LinkedList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.Map;
import java.util.HashMap;
import java.util.TreeSet;
import java.util.Collection;
import java.util.Queue;
import java.util.Properties;

// The codes below are largely based on http://www.grpc.io/docs/tutorials/basic/java.html.

public class NlpServer {
    private static final Logger logger = Logger.getLogger(NlpServer.class.getName());
    private final int port;
    private final int maxConcurrentCalls;
    private final int maxParseSeconds;
    private final int bllipParserPort;
    private final String bllipParserHost;

    private Server server;

    public NlpServer(int port, int maxConcurrentCalls, int maxParseSeconds, String bllipParserHost, int bllipParserPort) {
        this.port = port;
        this.maxConcurrentCalls = maxConcurrentCalls;
        this.maxParseSeconds = maxParseSeconds;
        this.bllipParserHost = bllipParserHost;
        this.bllipParserPort = bllipParserPort;
    }

    /**
     * Start serving requests.
     */
    public void start() throws IOException {
        server = NettyServerBuilder.forPort(port).maxConcurrentCallsPerConnection(maxConcurrentCalls)
                .addService(NlpServiceGrpc.bindService(new StanfordService(maxParseSeconds,
                        bllipParserHost, bllipParserPort)))
                .build()
                .start();
        logger.info("Server started, listening on " + port + ", max concurrent calls: " + maxConcurrentCalls);
        logger.info("Max parsing seconds: " + maxParseSeconds);
        Runtime.getRuntime().addShutdownHook(new Thread() {
            @Override
            public void run() {
                // Use stderr here since the logger may has been reset by its JVM shutdown hook.
                System.err.println("*** shutting down gRPC server since JVM is shutting down");
                NlpServer.this.stop();
                System.err.println("*** server shut down");
            }
        });
    }

    /**
     * Stop serving requests and shutdown resources.
     */
    public void stop() {
        if (server != null) {
            server.shutdown();
        }
    }

    /**
     * Await termination on the main thread since the grpc library uses daemon threads.
     */
    private void blockUntilShutdown() throws InterruptedException {
        if (server != null) {
            server.awaitTermination();
        }
    }

    public static void main(String[] args) {
        // Two command-line arguments, the listening port and max concurrent calls.
        int port = Integer.parseInt(args[0]);
        int maxConcurrentCalls = Integer.parseInt(args[1]);
        int maxParseSeconds = Integer.parseInt(args[2]);
        String bllipParserHost = args[3];
        int bllipParserPort = Integer.parseInt(args[4]);
        NlpServer server = new NlpServer(port, maxConcurrentCalls, maxParseSeconds,
                bllipParserHost, bllipParserPort);
        try {
            server.start();
            server.blockUntilShutdown();
        } catch (InterruptedException e) {
            System.exit(1);
        } catch (IOException e) {
            System.exit(1);
        }
    }

    private static class StanfordService implements NlpServiceGrpc.NlpService {
        private static final Logger logger = Logger.getLogger(StanfordService.class.getName());
        private final int maxParseSeconds;
        private final String bllipParserHost;
        private final int bllipParserPort;
        private final StanfordUtil sdutil;
        private BllipClient client;

        StanfordService(int maxParseSeconds, String bllipParserHost, int bllipParserPort) {
            this.maxParseSeconds = maxParseSeconds;
            this.bllipParserHost = bllipParserHost;
            this.bllipParserPort = bllipParserPort;
            // Load stanford util.
            sdutil = new StanfordUtil("tokenize, ssplit, pos, lemma, parse", maxParseSeconds);
        }

//        @Override
        public void processDocument(RpcProto.Request request, StreamObserver<RpcProto.Response> responseObserver) {
            RpcProto.Response.Builder rbuilder = RpcProto.Response.newBuilder();
            rbuilder.setSuccess(true);
            RpcProto.Request.RequestType requestType = request.getRequestType();
            for (DocumentProto.Document doc : request.getDocumentList()) {
                try {
                    if (requestType == RpcProto.Request.RequestType.SPLIT) {
                        rbuilder.addDocument(sdutil.splitSentence(doc));
                    } else if (requestType == RpcProto.Request.RequestType.PARSE_STANFORD) {
                        rbuilder.addDocument(sdutil.parseUsingStanford(doc));
                    } else if (requestType == RpcProto.Request.RequestType.PARSE_BLLIP) {
                        client = new BllipClient(bllipParserHost, bllipParserPort);
                        Map<String, String> sentences = sdutil.splitSentence(doc.getText());
                        Map<String, String> parses = client.parse(sentences);
                        DocumentProto.Document postDoc = sdutil.parseUsingBllip(doc, sentences, parses);
                        rbuilder.addDocument(postDoc);
                    }
                } catch (NullPointerException e) {
                    // System.out.println("NullPointerException caught");
                    // rbuilder.addAllDocument(request.getDocumentList());
                    // rbuilder.setSuccess(false);
                    // If timeouts, add the original document.
                    // Clear tokens and sentences which may contain incomplete results.
                    DocumentProto.Document.Builder dbuilder = doc.toBuilder();
                    dbuilder.clearToken();
                    dbuilder.clearSentence();
                    rbuilder.addDocument(dbuilder);
                }
            }
            responseObserver.onNext(rbuilder.build());
            responseObserver.onCompleted();
        }
    }
}
