<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:atom="http://www.w3.org/2005/Atom"
    xmlns:rz="http://repoze.org/namespace" exclude-result-prefixes="atom rz"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:key name="getsubentry" match="atom:entry" use="atom:content/rz:logentry/rz:request/@tid"/>
    <xsl:output method="html" indent="yes"/>
    <xsl:param name="items-style">flat</xsl:param>
    <xsl:template match="/">
        <xsl:choose>
            <xsl:when test="$items-style='tree'">
                <!-- Hierarchical listing -->
                <xsl:apply-templates select="atom:feed" mode="tree"/>
            </xsl:when>
            <xsl:otherwise>
                <!-- Flat listing, no hierarchy -->
                <xsl:apply-templates select="atom:feed" mode="flat"/>                
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    <xsl:template match="/atom:feed" mode="flat">
        <div>
            <xsl:apply-templates select="atom:entry" mode="item"/>
        </div>
    </xsl:template>
    <xsl:template match="atom:entry" mode="item">
        <!-- Used by both flat and tree modes -->
        <div class="tree-item-entry">
            <a href="{atom:id}">
                <xsl:value-of select="atom:title"/>
            </a>
        </div>
    </xsl:template>
    <!-- 
    
    Tree representation, ignore for now.
    
    -->
    <xsl:template match="/atom:feed" mode="tree">
        <div>
            <xsl:apply-templates select="atom:entry[atom:content/rz:logentry/rz:response/@tid]"
                mode="tree-group"/>
        </div>
    </xsl:template>
    <xsl:template match="atom:entry" mode="tree-group">
        <!-- The parent request is the one with a @tid on the response -->
        <div class="tree-group">
            <xsl:apply-templates select="." mode="item"/>
            <xsl:variable name="thistid" select="atom:content/rz:logentry/rz:response/@tid"/>
            <div class="tree-item">
                <xsl:apply-templates select="key('getsubentry', $thistid)" mode="item"/>
            </div>
        </div>
    </xsl:template>
</xsl:stylesheet>
