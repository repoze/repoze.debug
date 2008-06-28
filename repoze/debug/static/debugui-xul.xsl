<?xml version="1.0" encoding="UTF-8"?>
<!-- Convert the feed into various representations used for 
Firefox 3 XML datasources attached to XUL trees and whatnot. -->
<xsl:stylesheet xmlns:atom="http://www.w3.org/2005/Atom" exclude-result-prefixes="atom"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:template match="/">
        <log>
            <xsl:for-each select="/atom:feed/atom:entry">
                <entry entryid="{atom:id}" name="/somerequest.html" elapsed="22.0">
                    <item entryid="{atom:id}-1" name="App Result" elapsed="4.3"/>
                    <item entryid="{atom:id}-2" name="Siteconfig" elapsed="3.9"/>
                    <item entryid="{atom:id}-3" name="User" elapsed="0.8"/>
                </entry>
            </xsl:for-each>
        </log>
    </xsl:template>
</xsl:stylesheet>
