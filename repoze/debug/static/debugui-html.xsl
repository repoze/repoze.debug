<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:atom="http://www.w3.org/2005/Atom"
    xmlns:rz="http://repoze.org/namespace" exclude-result-prefixes="atom rz"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:key name="getsubentry" match="atom:entry" use="atom:content/rz:entry/rz:request/@tid"/>
    <xsl:output method="html" indent="yes"/>
    <xsl:template match="/atom:feed">
        <div>
            <xsl:apply-templates select="atom:entry[atom:content/rz:entry/rz:response/@tid]"
                mode="entry"/>
        </div>
    </xsl:template>
    <xsl:template match="atom:entry" mode="entry">
        <!-- The parent request is the one with a @tid on the response -->
        <div class="tree-entry">
            <xsl:apply-templates select="." mode="item"/>
            <xsl:variable name="thistid" select="atom:content/rz:entry/rz:response/@tid"/>
            <div class="tree-item"><xsl:apply-templates select="key('getsubentry', $thistid)" mode="item"/></div>
        </div>
    </xsl:template>
    <xsl:template match="atom:entry" mode="item">
        <!-- The parent request is the one with a @tid on the response -->
            <div class="tree-item-entry">
                <a href="{atom:id}">
                    <xsl:value-of select="atom:title"/>
                </a>
        </div>
    </xsl:template>
</xsl:stylesheet>
