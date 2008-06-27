
var processor;

function asxml (node) {
    var xmlString = new XMLSerializer().serializeToString(node);
    return xmlString;
}

function reloadFeed () {
    var url = "http://localhost:8090/foo/++debugui++/feed.xml";
    var xmlhttp = new XMLHttpRequest();  
    xmlhttp.open("GET", url, false);  
    xmlhttp.send('');  
    var feeddoc = xmlhttp.responseXML;

    var frag = processor.transformToFragment(feeddoc, document);
    var target = document.getElementById("output");
    Sarissa.clearChildNodes(target);
    target.appendChild(frag);
}

function debuginit () {
    var xmlhttp = new XMLHttpRequest();  
    xmlhttp.open("GET", "debugui.xsl", false);  
    xmlhttp.send('');  
    var xsldoc = xmlhttp.responseXML;
    processor = new XSLTProcessor();
    processor.importStylesheet(xsldoc);
}
