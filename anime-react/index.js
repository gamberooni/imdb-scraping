const express = require('express')
const app = express()
const hostAddress = 'localhost'
const serverPort = 8080
const reactPort = '3001'

const title_model = require('./title_model')

app.use(express.json())
app.use(function (req, res, next) {
  res.setHeader('Access-Control-Allow-Origin', `http://${hostAddress}:${reactPort}`);
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Access-Control-Allow-Headers');
  next();
});

app.get('/', (req, res) => {
    title_model.getTitles()
    .then(response => {
      res.status(200).send(response);
    })
    .catch(error => {
      res.status(500).send(error);
    })
  })

app.listen(serverPort, () => {
  console.log(`App running on port ${serverPort}.`)
})