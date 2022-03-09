function copyToClipboard(element) {
    var copyText = document.getElementById(element).innerHTML;

    var textBox = document.querySelector(".clipboard");
    textBox.setAttribute('value',copyText );

    textBox.select();
    document.execCommand('copy');
    textBox.setAttribute('value',"");
  }

function goBack(){
    window.history.back();
}

function calculateShipping() {

    var numOne = document.getElementById('weight_value').value;
    var numTwo = document.getElementById('price_per_kg').value;

    //console.log("Number One",numOne)
    //console.log("Number Two",numTwo)

    var theProduct = parseFloat(numOne) * parseFloat(numTwo);
    var theProduct = Math.ceil(theProduct)

    // document.write(theProduct);
    // document.write(theTotal);


    document.getElementById("shipping_value").value = theProduct
  
}

function calculatePAmount(){
    var amount = document.getElementById('inputPAmount').value;
    var exchange = document.getElementById('inputPExchange').value;

    console.log("The amount is",amount)
    console.log("The amount exchange rate is",exchange)


    var theProduct = parseFloat(amount) * parseFloat(exchange);
    var theProduct = Math.ceil(theProduct)

    document.getElementById("inputAmountKES").value = theProduct
}


var toastLiveExample = document.getElementById('liveToast')

var toast = new bootstrap.Toast(toastLiveExample)

toast.show()

    
    



// jQuery(document).ready(function($) {
//   $(".clickable-row").click(function() {
//       window.location = $(this).data("href");
//   });
// });






