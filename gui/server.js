const express = require('express');
const multer = require('multer');
const fs = require('fs');
const app = express();
const upload = multer({ dest: 'gui/uploads/' });
const path = require('path')
app.use(express.static('public'));

app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/register', upload.single('imageUpload'), function (req, res, next) {
    const firstName = req.body.firstName;
    const middleName = req.body.middleName;
    const lastName = req.body.lastName;
    const phone = req.body.phone;
    const dob = req.body.dob;
    const imagePath = req.file.path;
    const originalExtension = path.extname(req.file.originalname);

    const newPath = `C:/Users/ranad/OneDrive/Documents/GitHub/face_recognition_prog/gui/uploads/${firstName}-${lastName}-001${originalExtension}`;
    fs.rename(imagePath, newPath, function(err) {
        if (err) throw err;
        console.log('File Renamed!');
    });

    res.send('File uploaded and moved!');
});
app.listen(1100, function () {
    console.log('Example app listening on port 1100!')
});
