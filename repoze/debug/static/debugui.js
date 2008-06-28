
var processor;
var url = "../feed.xml";

function asxml (node) {
    return new XMLSerializer().serializeToString(node);
}


function geturl(url) {
    var xmlhttp = new XMLHttpRequest();  
    xmlhttp.open("GET", url, false);  
    xmlhttp.send('');  
    return xmlhttp.responseXML;
}


function reloadFeed () {
    var target = document.getElementById("tree");
    Sarissa.updateContentFromURI(url, target, processor);
}


function debuginit () {
    var xsldoc = geturl("debugui.xsl");
    processor = new XSLTProcessor();
    processor.importStylesheet(xsldoc);
}
