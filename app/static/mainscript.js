function mask_screen(){
    let masking = document.createElement('div')
    masking.setAttribute('class', 'masking')
    masking.setAttribute('style', 'width: 100%; height: 100%; background-color: #000000; opacity: 0.5; position: absolute; top: 0px; left: 0px; z-index: 9999; text-align: center;')
    masking.textContent = 'Calculating optimal tour'

    document.body.appendChild(masking)
}

function demask_screen(){
    let masking = document.getElementsByClassName('masking')

    document.body.removeChild(masking)
}

// function getresult_promise(){
//     return new Promise(function (resolve, reject){
//         let xhr = new XMLHttpRequest();
//         xhr.open("GET", "/searching");
//         xhr.send();

//         xhr.onload = function (){
//             if (xhr.status === 200){
//                 resolve(xhr.response)
//             }
//             else{
//                 reject(new Error(xhr.status))
//             }
//         }
//     });
// }

async function getgaModuleresult(){
    if (document.getElementById('starttime').value !== ""){
        mask_screen()

        let data = {
            starttime: document.getElementById('starttime').value
        }

        let searching = await fetch("http://192.168.1.3:80/searching", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(result=>'받은 이미지를 html에 띄우기')

        demask_screen()
    }
    else{
        document.getElementById('starttime').style.cssText = "border: 2px solid red;"
    }
}

async function adddest(){
    if (document.getElementsByClassName('input')[0].value !== ""
    && document.getElementsByClassName('input')[1].value !== ""
    && document.getElementsByClassName('input')[2].value !== ""
    && document.getElementsByClassName('input')[3].value !== ""
    && document.getElementsByClassName('input')[4].value !== ""
    && document.getElementsByClassName('input')[5].value !== ""){
        let data = {
            lon: document.getElementById('lon').value,
            lat: document.getElementById('lat').value,
            util: document.getElementById('util').value,
            stay: document.getElementById('stay').value,
            open: document.getElementById('open').value,
            close: document.getElementById('close').value
        }
        
        let adding = await fetch("http://192.168.1.3:80/adding", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(response => '받은리스트를destbox에 띄우기')

    }
    else{
        alert('please complete the input form.')
    }
}

async function resetdest(){
    let reset = await fetch("http://192.168.1.3:80/reset", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data) //이부분 고치기 data가 있을수 없으니
    })
    .then(response => '받은리스트를destbox에 띄우기')
}