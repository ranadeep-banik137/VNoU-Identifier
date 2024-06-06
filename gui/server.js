const express = require('express');
const multer = require('multer');
const fs = require('fs');
const app = express();
const upload = multer({ dest: 'gui/uploads/' });
const path = require('path');

app.use(express.static('.'));

app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/register', upload.single('imageUpload'), function (req, res, next) {
    const firstName = req.body.firstName;
    const lastName = req.body.lastName;
    const imagePath = req.file.path;
    const originalExtension = path.extname(req.file.originalname);
    const newPath = `D:/Projects/VNoU-Identifier/gui/uploads/${firstName}-${lastName}-001${originalExtension}`;

    // Function to rename the file with retry logic
    const renameFile = (oldPath, newPath, retries = 5) => {
        fs.rename(oldPath, newPath, function(err) {
            if (err) {
                if ((err.code === 'EBUSY' || err.code === 'ENOENT') && retries > 0) {
                    // Retry after a short delay
                    setTimeout(() => renameFile(oldPath, newPath, retries - 1), 100);
                } else {
                    // If retries exhausted or another error, pass the error to the next middleware
                    return next(err);
                }
            } else {
                console.log('File Renamed!');
                res.send('File uploaded and moved!');
            }
        });
    };

    // Function to check if the file is ready to be renamed
    const waitForFile = (filePath, callback, retries = 10) => {
        if (fs.existsSync(filePath)) {
            callback();
        } else {
            setTimeout(() => {
                if (retries > 0) {
                    waitForFile(filePath, callback, retries - 1);
                } else {
                    next(new Error('File does not exist'));
                }
            }, 100);
        }
    };

    // Wait for the file to be ready and then rename it
    waitForFile(imagePath, () => renameFile(imagePath, newPath));
});

app.listen(1100, function () {
    console.log('Example app listening on port 1100!');
});
