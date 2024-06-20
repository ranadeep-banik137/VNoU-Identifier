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
    const middleName = req.body.middleName || '';
    const email = req.body.email || '';
    const phone = req.body.phone || '';
    const imagePath = req.file.path;
    const originalExtension = path.extname(req.file.originalname);
    const randomNum = Math.floor(Math.random() * 1000);
    const newFileName = `VNoU-${randomNum}`;
    const newFile = `gui/uploads/${newFileName}${originalExtension}`;

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
                const data = {
                    'first_name': firstName,
                    'last_Name': lastName,
                    'middle_Name': middleName || '',
                    'email': email || '',
                    'phone': phone || ''
                };
                const textFilePath = `gui/uploads/details.yml`;
                const yamlData = `${newFileName}:\n` + Object.entries(data)
                    .map(([key, value]) => {
                        if (value !== '') {
                            return `\t${key}: ${value}`;
                        } else {
                            return `\t${key}: ''`; // Represent empty values as ''
                        }
                    })
                    .join('\n') + '\n\n';

                fs.appendFile(textFilePath, yamlData, function(err) {
                    if (err) {
                        return next(err); // Pass error to Express error handler
                    }
                    console.log('Text file updated:', textFilePath);
                    res.send('File uploaded, moved, and data saved!');
                });
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
    waitForFile(imagePath, () => renameFile(imagePath, newFile));
});

app.listen(1100, function () {
    console.log('Example app listening on port 1100!');
});
