const express = require('express');
const app = express();
const cors = require('cors'); // Cross-origin resource sharing
const appOS = require('../lib/app');
const fs = require('fs');
//const path = require('path');

// Settings
const Port = '8000';
const FileCreatePartStudio = `${__dirname}/database/dataFile.json`;
const storageFileStl = `${__dirname}/storage-file-stl/data.stl`;

// Config dotenv
const myKeys = require('../config/apikey.js');
app.use(cors({ origin: `http://localhost:${Port}` }));


app.get('/', function (req, res) {
  res.send("Hello World");
});


app.get('/stl', function (req, res) {
  const stl = appOS.partStudioStl(
    myKeys.document_Id, myKeys.workspace_W_Id, myKeys.workspace_E_Id, { mode: 'string' },
    function (data) {

      // Create file in folder storage-file-stl
      fs.writeFileSync(storageFileStl, data,
        function (err) {
          if (err) throw err;
          console.log('The file has been saved!  data.stl');
        });

      //console.log(data.toString());
      res.send(data);
    }
  );
});


app.get('/createPartStudio', function (req, res) {

  const newPartStudio = 'name of the new PartStudio';
  const Part_Studio = appOS.createPartStudio(
    myKeys.document_Id, myKeys.workspace_W_Id, newPartStudio, function (data) {

      // Example
      let new_Part_Studio = {};
      new_Part_Studio = JSON.parse(data.toString());
      //console.log('the id is: ' + new_Part_Studio.id); // Example of how to access the Part Studio id


      // Create & write file in folder storage-file
      fs.appendFile(FileCreatePartStudio, data + `,\n`,
        function (err) {
          if (err) return console.log(err);
          console.log('The file has been saved!  dataFile.json');
        });

      // console.log(data.toString());
      res.send(data);
    }
  );
});


app.get('/deleteElement', function (req, res) {
  //Nuber id for example->  3ad02ac46a847ed284d8694c
  const deleteElement_ = '3ad02ac46a847ed284d8694c';

  const DeleteElement = appOS.deleteElement(
    myKeys.document_Id, myKeys.workspace_W_Id, deleteElement_,
    function (data) {
      //console.log(data.toString());
      res.send(data);
    }
  );
});

app.get('/info', function (req, res) {

  if(true){
  res.end(
  `<html>
  <head>
      <title>Document</title>
  </head>
  <body>
      <h1  style="text-align:center">info</h1>
      <p  style="text-align:center">
      This is a small example with three methods:<br>
      /stl<br>
      /createPartStudio<br>
      /deleteElement<br><br>
      Plus an info method that shows some html<br>
      /info
      </p><br>
  
  </body>
  </html>` );
  }
  else{
    // path -> public/index.html 
    // res.sendFile('index.html');
  }
 
});


app.listen(Port, () => {
  console.log(`Express Running on Port ${Port} \n\nhttp://localhost:${Port}/`)
});
