FROM amazonlinux:2 as base

# Tips
# Cleanup everything
# docker system prune
# Build:
# DOCKER_BUILDKIT=1 docker build -t genny .
# Evaluate:
# docker run --mount type=bind,source=/home/ubuntu/genny/workload,target=/genny/dist/etc/genny/workloads/  --mount type=bind,source=/home/ubuntu/genny/src/phases,target=/genny/dist/etc/genny/phases  genny evaluate workload/UpdateOnly-es1-0-16-16.yml
# Run:
# docker run --mount type=bind,source=/home/ubuntu/genny/workload,target=/genny/dist/etc/genny/workloads/  --mount type=bind,source=/home/ubuntu/genny/src/phases,target=/genny/dist/etc/genny/phases --network host  genny workload -u localhost:27017 dist/etc/genny/workloads/UpdateOnly-es1-0-16-16.yml

RUN yum -y groupinstall Development Tools
RUN yum -y install python3 python3-pip sudo bash git

ENV USER="root"
RUN curl http://mongodbtoolchain.build.10gen.cc/installer.sh | bash

RUN mkdir -p /{data/mci,genny}
WORKDIR /genny

RUN mkdir -p /genny/build/curator
RUN curl https://s3.amazonaws.com/boxes.10gen.com/build/curator/curator-dist-rhel70-3df28d2514d4c4de7c903d027e43f3ee48bf8ec1.tar.gz | tar -xvzf - -C /genny/build/curator

FROM base as build

RUN mkdir -p /data/mci/gennytoolchain
RUN curl https://s3.amazonaws.com/mciuploads/genny-toolchain/genny_toolchain_amazon2_b563d3ba01a8b1a4fa4249e9eb0ad5c9bc11816b_22_12_12_21_24_44/gennytoolchain.tgz | tar -xvzf - -C /data/mci/gennytoolchain

ADD . .
RUN ./run-genny install -d amazon2

FROM base
RUN mkdir -p /data/workdir/mongocrypt/
RUN curl https://mciuploads.s3.amazonaws.com/mongodb-mongo-master/mongo_crypt/linux-x86-dynamic-compile-required/b206e0264580e726f2ba4063a435ded5de28d9a2/mongo_crypt_shared_v1-6.3.0-alpha-492-gb206e02.tgz | tar -xvzf - -C /data/workdir/mongocrypt

COPY --from=build /genny /genny
COPY --from=build /data/mci/gennytoolchain/installed/x64-linux-dynamic/lib/ /data/mci/gennytoolchain/installed/x64-linux-dynamic/lib/

ENTRYPOINT ["/genny/run-genny"]
CMD ["-h"]