
var url = "../feed.xml";
var treeid = "xui-logtree";
var processor;
var atomdoc;

function asxml (node) {
    return new XMLSerializer().serializeToString(node);
}


function geturl(url) {
    var xmlhttp = new XMLHttpRequest();  
    xmlhttp.open("GET", url, false);  
    xmlhttp.send('');  
    return xmlhttp.responseXML;
}


function documentLoaded (e) {
    var tree = document.getElementById(treeid);
    tree.builder.rebuild();

    // Mark the first item as selected
    tree.view.selection.select(0);
    tree.view.toggleOpenState(0);
}

function selectEntry () {
    var tree = document.getElementById(treeid);
    var item = tree.view.getItemAtIndex(tree.currentIndex);
    var hrefcell = item.childNodes[0].childNodes[2];
    if (hrefcell.hasAttribute("label")) {
	// Change the browser url on the right
	var href = hrefcell.getAttribute("label");
	var iframe = document.getElementById("selected-entry");
	iframe.setAttribute("src", href);
    }
}


function reloadSummary () {
    /* Transform to make XUL trees with XML datasources easier */

    // Grab the target, which is the document element on the tree
    var tree = document.getElementById(treeid);
    var target = tree.builder.datasource.documentElement;

    // Get new data, transform it, and import into the document
    var result = processor.transformToDocument(geturl("samplefeed.xml"));
    var iresult = document.importNode(result.documentElement, true);

    // Update the tree datasource and rebuild
    Sarissa.moveChildNodes(iresult, target);
    tree.builder.rebuild();
}

function init () {
    var xsldoc = geturl("debugui-xul.xsl");
    processor = new XSLTProcessor();
    processor.importStylesheet(xsldoc);
}

document.addEventListener("DOMContentLoaded", init, false);
