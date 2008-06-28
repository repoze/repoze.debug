
var gm;

function GuiModel (treeid, atomurl) {
    this.treeid = treeid;
    this.atomurl = atomurl;
    this.tree = document.getElementById(treeid);
    this.processor = null;
    this.atomdoc = null;
}

GuiModel.prototype.tostring = function (node) {
    /* Dump a document or node to a string representation */

    var s = new XMLSerializer();
    return s.serializeToString(node);
}


GuiModel.prototype.loadURL = function (url) {
    /* Synchronously load some XML, return the document element */

    var xmlhttp = new XMLHttpRequest();  
    xmlhttp.open("GET", url, false);  
    xmlhttp.send('');
    return xmlhttp.responseXML;
}

GuiModel.prototype.loadProcessor = function (xslurl) {
    /* Load the XSLT that massages Atom-data into XML datasources */

    this.xsldoc = this.loadURL(xslurl);
    this.processor = new XSLTProcessor();
    this.processor.importStylesheet(this.xsldoc);
}


GuiModel.prototype.reloadModel = function () {
    /* Fetch the atom data, then update various trees */

    // Grab the target, which is the document element on the tree
    var target = this.tree.builder.datasource.documentElement;

    // Get new data, transform it, and import into the document
    var atomdoc = this.loadURL(this.atomurl);
    var result = this.processor.transformToDocument(atomdoc);
    var iresult = document.importNode(result.documentElement, true);

    // Update the tree datasource and rebuild
    Sarissa.moveChildNodes(iresult, target);
    this.tree.builder.rebuild();
}

function documentLoaded (e) {
    var tree = document.getElementById(treeid);
    tree.builder.rebuild();

    // Mark the first item as selected
    tree.view.selection.select(0);
    tree.view.toggleOpenState(0);
}


function initGuiModel () {
    if (window.location.host.indexOf(":") == -1){
	// Running from FS, not dynamicall via WSGI, use dummy data
	var atom_url = "samplefeed.xml";
    } else {
	var atom_url = "../feed.xml";
    }
    gm = new GuiModel("xui-logtree", atom_url);
    gm.loadProcessor("debugui-xul.xsl");
    gm.reloadModel();
    return;
    var xsldoc = geturl("debugui-xul.xsl");
    processor = new XSLTProcessor();
    processor.importStylesheet(xsldoc);
}

document.addEventListener("DOMContentLoaded", initGuiModel, false);


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

