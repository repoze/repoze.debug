<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:atom="http://www.w3.org/2005/Atom"
    exclude-result-prefixes="atom" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="html" indent="yes"/>
    <xsl:template match="/atom:feed">
        <h1>
            <xsl:value-of select="atom:title"/>
        </h1>
        <div>
            <em>Last Updated: <xsl:value-of select="atom:updated"/></em>
        </div>
        <ul>
            <xsl:for-each select="atom:entry">
                <li>Item: <xsl:value-of select="atom:title"/></li>
            </xsl:for-each>
        </ul>
    </xsl:template>
</xsl:stylesheet>
