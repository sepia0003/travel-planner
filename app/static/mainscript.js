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

async function getgaModuleresult(){
    if (document.getElementById('starttime').value !== ""){
        mask_screen()

        let data = {
            starttime: document.getElementById('starttime').value
        }

        await fetch("http://192.168.1.3:80/searching", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(result=>'받은 이미지를 html에 띄우기') //folium으로 만든 html지도를 flask에서 문자열로 받아와서 그걸 오른쪽 section에 띄우도록해보자

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
        
        await fetch("http://192.168.1.3:80/adding", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data) //body에 문자열을 실어보내는것이다. JSON.stringify()는 문자열이다
        })
        .then(response => response.json()) //서버에서 온 응답인 response는 method, headers, body 등의 정보가 들어있는 리스폰스객체이기때문에 response에 .json()메소드를 사용해서 json부분만을 딕셔너리객체로 가져오는것을 결과로 이행하는 또다른 프로미스를 반환함.
        .then(data => { //data는 {"data": [{1row의 key:val, ...}, {2row의 key:val, ...}]}의 딕셔너리객체
            const destbox = document.getElementById('destbox')
            while (destbox.firstChild){
                destbox.removeChild(destbox.firstChild)
            }
            temp = data["data"] //temp는 [{1row의 key:val, ...}, {2row의 key:val, ...}] 리스트
            for (let i=0; i<temp.length; i++){
                let dest = document.createElement('div')
                // dest.setAttribute('class', 'masking')
                // dest.setAttribute('style', 'width: 100%; height: 100%; background-color: #000000; opacity: 0.5; position: absolute; top: 0px; left: 0px; z-index: 9999; text-align: center;')
                dest.textContent = Object.values(temp[i])       //values의 값들이 뒤죽박죽인 상태 고쳐야함
                destbox.append(dest)
            }
        })

    }
    else{
        alert('please complete the input form.')
    }
}

async function resetdest(){
    await fetch("http://192.168.1.3:80/reset")       
    .then()
    const destbox = document.getElementById('destbox')
    while (destbox.firstChild){
        destbox.removeChild(destbox.firstChild)
    }
}