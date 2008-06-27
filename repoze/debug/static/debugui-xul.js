
/* */
var url = "/++xui++/data/summary.xml";
var treeid = "xui-logtree";

function asxml (node) {

    var serializer = new XMLSerializer();
    var xml = serializer.serializeToString(node);
    return xml;
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
    var tree = document.getElementById(treeid);
    var xmlDoc = tree.builder.datasource;
        
    xmlDoc.addEventListener("load", documentLoaded, false);
    xmlDoc.load(url);
}

function init () {
    /* */
}

document.addEventListener("DOMContentLoaded", init, false);
