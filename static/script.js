async function uploadPDF(){

    const pdf=document.getElementById("pdf").files[0];

    if(!pdf){
        alert("Please choose a PDF");
        return;
    }

    const formData=new FormData();

    formData.append("pdf",pdf);

    document.getElementById("loading").innerHTML="Uploading PDF...";

    const response=await fetch("/upload",{
        method:"POST",
        body:formData
    });

    const data=await response.json();

    document.getElementById("loading").innerHTML="";

    alert(data.message);
}


async function askQuestion(){

    const question=document.getElementById("question").value;

    if(question===""){
        alert("Enter your question");
        return;
    }

    document.getElementById("loading").innerHTML="Thinking...";

    const response=await fetch("/ask",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            question:question
        })

    });

    const data=await response.json();

    document.getElementById("loading").innerHTML="";

    document.getElementById("answer").innerHTML=data.answer;

}