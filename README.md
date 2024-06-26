<h1 align="center">Hi 👋, I'm Ranadeep Banik</h1>
<h3 align="center">The name of this app is VNoU (Sounds familiar as WE KNOW YOU!). It maintains/records data in storage (encoded) and through the camera device installed, it verifies the same person's activity/presence and record logs</h3>
<h4 align="center">The face recognition is done applying different models (pre-trained)</h4>
<h5 align="left">- 💻 mtcnn : It is slight faster and will capture accurate faces but has to be in proper position of camera</h5> 
<h5 align="left">- 💻 cascade : it uses hog model which is very fast but lack in accuracy (uses haarcascade_frontalface_default.xml to detect face)</h5>
<h5 align="left">- 💻 VNoU(Our own trained model) : Very fast and 90% accurate assembled with various face conditions (A little tilted/frontal/left/right identification)</h5>

<h6 align="center">Note: There are adjustments needed to be done in configuration based on camera types and lighting for the face detection accuracy </h6>

<h8 align="left">face_config: </h8>

<h9 align="left">1. img-blur-threshold-percentage should be 20 (ideal for webcam)</h9>

<h9 align="left">2. img-tilt-threshold-angle should be 10 (ideal for normal tilt-ness of face)</h9>

<h7 align="left">For the laplacian image, it is edged image. Make images using GaussianBlur with different r, then do laplacian filter on them, and calculate the vars:</h7>

<p align="center"> <img src="https://i.sstatic.net/aS7YF.jpg"/></p>

<h5 align="left">The blured image's edge is smoothed, so the variance is little.</h5>

<h7 align="left">Example Threshold Values for recognizing face (Refer to ['face_recognition']['face-distance-threshold'] in configmap):</h7>

<h9 align="left">1.Strict Threshold: 0.5 or lower. Use this if your application requires very high accuracy and can tolerate higher computational demands.</h9>

<h9 align="left">2. Moderate Threshold: 0.6 to 0.7. This is suitable for many general-purpose face recognition applications where accuracy and performance need to be balanced.</h9>

<h9 align="left">3. Lenient Threshold: 0.8 or higher. Use this if your application prioritizes performance over strict accuracy, or if the consequences of false positives are minimal.</h9>

<p align="left"> <img src="https://komarev.com/ghpvc/?username=ranadeep-banik137&label=Profile%20views&color=0e75b6&style=flat" alt="ranadeep-banik137" /> </p>

<p align="left"> <a href="https://github.com/ryo-ma/github-profile-trophy"><img src="https://github-profile-trophy.vercel.app/?username=ranadeep-banik137" alt="ranadeep-banik137" /></a> </p>

- 👨‍💻 All of my projects are available at [ranadeep-banik137/projects](ranadeep-banik137/projects)

- 📫 How to reach me **ranadeep.banik137@yahoo.com**

<h3 align="left">Connect with me:</h3>
<p align="left">
<a href="https://fb.com/https://www.facebook.com/ranadeep.banik" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/facebook.svg" alt="https://www.facebook.com/ranadeep.banik" height="30" width="40" /></a>
<a href="https://instagram.com/https://www.instagram.com/r.d.b_here/" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/instagram.svg" alt="https://www.instagram.com/r.d.b_here/" height="30" width="40" /></a>
</p>

<h3 align="left">Languages and Tools:</h3>
<p align="left"> <a href="https://angular.io" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/angularjs/angularjs-original-wordmark.svg" alt="angularjs" width="40" height="40"/> </a> <a href="https://aws.amazon.com" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/amazonwebservices/amazonwebservices-original-wordmark.svg" alt="aws" width="40" height="40"/> </a> <a href="https://www.w3schools.com/css/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original-wordmark.svg" alt="css3" width="40" height="40"/> </a> <a href="https://git-scm.com/" target="_blank" rel="noreferrer"> <img src="https://www.vectorlogo.zone/logos/git-scm/git-scm-icon.svg" alt="git" width="40" height="40"/> </a> <a href="https://golang.org" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/go/go-original.svg" alt="go" width="40" height="40"/> </a> <a href="https://www.w3.org/html/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original-wordmark.svg" alt="html5" width="40" height="40"/> </a> <a href="https://www.linux.org/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/linux/linux-original.svg" alt="linux" width="40" height="40"/> </a> <a href="https://www.mysql.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/mysql/mysql-original-wordmark.svg" alt="mysql" width="40" height="40"/> </a> <a href="https://nodejs.org" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/nodejs/nodejs-original-wordmark.svg" alt="nodejs" width="40" height="40"/> </a> <a href="https://opencv.org/" target="_blank" rel="noreferrer"> <img src="https://www.vectorlogo.zone/logos/opencv/opencv-icon.svg" alt="opencv" width="40" height="40"/> </a> <a href="https://pandas.pydata.org/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/2ae2a900d2f041da66e950e4d48052658d850630/icons/pandas/pandas-original.svg" alt="pandas" width="40" height="40"/> </a> <a href="https://www.postgresql.org" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original-wordmark.svg" alt="postgresql" width="40" height="40"/> </a> <a href="https://www.python.org" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/> </a> <a href="https://pytorch.org/" target="_blank" rel="noreferrer"> <img src="https://www.vectorlogo.zone/logos/pytorch/pytorch-icon.svg" alt="pytorch" width="40" height="40"/> </a> <a href="https://reactjs.org/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/react/react-original-wordmark.svg" alt="react" width="40" height="40"/> </a> <a href="https://www.selenium.dev" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/detain/svg-logos/780f25886640cef088af994181646db2f6b1a3f8/svg/selenium-logo.svg" alt="selenium" width="40" height="40"/> </a> </p>
