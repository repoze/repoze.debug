
var gm;
var cl = console.log;

function GuiModel (tree_id, atom_url) {
    this.tree_id = tree_id;
    this.atom_url = atom_url;
    this.tree = document.getElementById(tree_id);
    this.processor = null;
    this.atom_doc = null;
    this.curr_tree_selection = 0;
    this.ns = {
	'xhtml' : 'http://www.w3.org/1999/xhtml',
	'mathml': 'http://www.w3.org/1998/Math/MathML',
	'atom'  : 'http://www.w3.org/2005/Atom',
    };


    // Register handlers
    this.tree.addEventListener("select", this.selectEntry, false);
    var btn = document.getElementById("reloadEntries");
    btn.addEventListener("command", this.reloadModel, false);
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
    this.atom_doc = this.loadURL(this.atom_url);
    var result = this.processor.transformToDocument(this.atom_doc);
    var iresult = document.importNode(result.documentElement, true);

    // Update the tree datasource and rebuild
    Sarissa.moveChildNodes(iresult, target);
    this.tree.builder.rebuild();

    // Reset the selection to the last-known selection
    this.tree.view.selection.select(this.curr_tree_selection);
    this.tree.view.toggleOpenState(this.curr_tree_selection);
}


GuiModel.prototype.selectEntry = function (e) {
    /* Activate the right-hand side */

    var item = gm.tree.view.getItemAtIndex(gm.tree.currentIndex);
    var entrynode = item.getElementsByClassName("entryid")[0];
    var entryid = entrynode.getAttribute("label");
    gm.curr_entryid = entryid;
    gm.curr_tree_selection = gm.tree.view.selection.currentIndex;

    // Change the browser url on the right
    var this_id = "urn:uuid:32736";
    var xp = "/*/atom:entry[atom:id='" + entryid + "']/atom:link";
    var href= selectSingleNode(xp).getAttribute("href");
    var iframe = document.getElementById("selected-entry");
    iframe.setAttribute("src", href);

}


function initGuiModel () {
    /* Run on document load by the DOMContentLoaded listener below */

    if (window.location.host.indexOf(":") == -1){
	// Running from FS, not dynamicall via WSGI, use dummy data
	var atom_url = "samplefeed.xml";
    } else {
	var atom_url = "../feed.xml";
    }
    gm = new GuiModel("xui-logtree", atom_url);
    gm.loadProcessor("debugui-xul.xsl");
    gm.reloadModel();
}

document.addEventListener("DOMContentLoaded", initGuiModel, false);



/* Companion functions, stolen from Sarissa */

function selectNodes (sExpr, returnSingle) {
    var nsDoc = gm.atom_doc;
    function nsresolver(prefix) {
	return gm.ns[prefix] || null;
    }
    var result = null;
    if(!returnSingle){
        var oResult = nsDoc.evaluate(sExpr,
            nsDoc,
            nsresolver,
            XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        var nodeList = new SarissaNodeList(oResult.snapshotLength);
        nodeList.expr = sExpr;
        for(var i=0;i<nodeList.length;i++){
            nodeList[i] = oResult.snapshotItem(i);
        }
        result = nodeList;
    }
    else {
	var xf = XPathResult.FIRST_ORDERED_NODE_TYPE;
        result = nsDoc.evaluate(sExpr,
			       nsDoc,
			       nsresolver,
			       xf, null).singleNodeValue;
    }
    return result;      
};

function selectSingleNode (sExpr) {
    return selectNodes(sExpr, true);
}
 
function SarissaNodeList (i) {
    this.length = i;
};
