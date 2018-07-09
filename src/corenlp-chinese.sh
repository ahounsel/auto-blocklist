java -Xmx4g -cp "../lib/corenlp/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -threads 16 \
-serverProperties StanfordCoreNLP-chinese.properties \
-preload tokenize,ssplit \
-status_port 9001 -port 9001 -timeout 90000 \
