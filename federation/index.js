const { ApolloServer } = require("apollo-server");
const { ApolloGateway } = require("@apollo/gateway");

const serviceList = [
  {
    name: "saleor",
    url: "https://api.wecre8.ninja/graphql/",
  },
  {
    name: "social-login",
    url: "https://pr-32.herokuapp.com/plugins/social-login/graphql",
  }
];

const gateway = new ApolloGateway({ serviceList });

const server = new ApolloServer({
  gateway,
});

server
  .listen({ port: process.env.PORT || 4000 })
  .then(({ url }) => {
    console.log(`🚀  Gateway is ready at ${url}`);
  })
  .catch((err) => {
    console.error(err);
  });
