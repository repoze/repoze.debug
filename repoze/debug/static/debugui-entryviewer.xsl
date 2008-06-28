<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:atom="http://www.w3.org/2005/Atom" xmlns:rz="http://repoze.org/namespace"
    xmlns="http://www.w3.org/1999/xhtml" exclude-result-prefixes="atom rz"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:import href="xmlverbatim.xsl"/>
    <xsl:output indent="yes"/>
    <xsl:variable name="entryid" select="/atom:feed/@selected"/>
    <xsl:template match="/">
        <div><h1>kdkdkd</h1><xsl:apply-templates select="/atom:feed/atom:entry[atom:id=$entryid]"/></div>
    </xsl:template>
    <xsl:template match="atom:entry">
        <div>
            <h1>
                <xsl:value-of select="atom:title"/>
            </h1>
            <xsl:apply-templates select="." mode="xmlverb"/>
        </div>
    </xsl:template>
</xsl:stylesheet>
