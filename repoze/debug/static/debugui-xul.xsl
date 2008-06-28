<?xml version="1.0" encoding="UTF-8"?>
<!-- Convert the feed into various representations used for 
Firefox 3 XML datasources attached to XUL trees and whatnot. -->
<xsl:stylesheet xmlns:atom="http://www.w3.org/2005/Atom" exclude-result-prefixes="atom"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:template match="/">
        <log>
            <xsl:for-each select="/atom:feed/atom:entry">
                <entry id="n32432" name="/somerequest.html">
                    <item id="n32432" name="xxApp Result"/>
                    <item id="n32432" name="Siteconfig"/>
                    <item id="n32432" name="User"/>
                </entry>
            </xsl:for-each>
        </log>
    </xsl:template>
</xsl:stylesheet>
