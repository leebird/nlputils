A few java libraries are needed for the server. Download them and put the jar files under the folder ./lib, and then modify the paths in running and testing script if neccessary. If the following link doesn't provide jar file download, goto maven repository or compile it manually.

1. Stanford CoreNLP
- This library can be downloaded from http://stanfordnlp.github.io/CoreNLP/

2. protobuf-java
- This library should be found in dep/protobuf/java

3. grpc-java
- This library can be downloaded from https://github.com/grpc/grpc-java

4. neety.io
- This library can be downloaded from http://netty.io/
- Note that only netty>=4.1 has the required APIs. Now we use netty-4.1.0.Beta6.

5. hpack
- This library can be downloaded from https://github.com/twitter/hpack.git

6. guava
- This library can be downloaded from https://github.com/google/guava/

TODO: include support of Bllip parser.