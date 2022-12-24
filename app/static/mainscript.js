function mask_screen(){
    let targetarea = document.getElementsByTagName("body");

    let masking = document.createElement('div');
    masking.setAttribute('class', 'masking');
    masking.setAttribute('style', 'width: 100%; height: 100%; background-color: #000000; opacity: 0.5; position: absolute; top: 0px; left: 0px; z-index: 9999;');
    masking.textContent = 'Calculating optimal tour';

    document.body.appendChild(masking)
}

function demask_screen(){
    let targetarea = document.getElementsByTagName("body");
    
    let masking = document.getElementsByClassName('masking')

    document.body.removeChild(masking)
}