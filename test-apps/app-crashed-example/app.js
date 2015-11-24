window.addEventListener("load", function() {
  console.log("Hello World!");
});


// FOR LOOP JS TEST
function run() {
    var c = document.getElementById("content");
    var n = document.createElement("p");
    var i, j;
    var messsage;

    for (i = 1; i <= 9; i++) {

        // for (j = 1; j <= 9; j++) {
        for (;;) {

            n.appendChild(document.createTextNode(i * j + " "));
            c.appendChild(n);
        }
        n.appendChild(document.createElement("br"));
        c.appendChild(n);
    }
    
    }      