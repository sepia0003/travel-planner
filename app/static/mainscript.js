function mask_screen(){
    let masking = document.createElement('div');
    masking.setAttribute('class', 'masking');
    masking.setAttribute('style', 'width: 100%; height: 100%; background-color: #000000; opacity: 0.5; position: absolute; top: 0px; left: 0px; z-index: 9999; text-align: center;');
    masking.textContent = 'Calculating optimal tour';

    document.body.appendChild(masking)
}

function demask_screen(){
    let masking = document.getElementsByClassName('masking')

    document.body.removeChild(masking)
}

function getresult_promise(){
    return new Promise(function (resolve, reject){
        let xhr = new XMLHttpRequest();
        xhr.open("GET", "/searching");
        xhr.send();

        xhr.onload = function (){
            if (xhr.status === 200){
                resolve(xhr.response)
            }
            else{
                reject(new Error(xhr.status))
            }
        }
    });
}

async function getgaModuleresult(){
    mask_screen();

    let resultimage = await getresult_promise();

    let sectiontag = document.getElementsByClassName('mapscreen')
    sectiontag.appendChild(resultimage)
    demask_screen();
}