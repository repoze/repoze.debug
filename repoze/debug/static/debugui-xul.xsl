<?xml version="1.0" encoding="UTF-8"?>
<!-- Convert the feed into various representations used for 
Firefox 3 XML datasources attached to XUL trees and whatnot. -->
<xsl:stylesheet xmlns:atom="http://www.w3.org/2005/Atom" xmlns:rz="http://repoze.org/namespace"
    exclude-result-prefixes="atom rz" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output indent="yes"/>
    <xsl:key name="getsubentry" match="atom:entry" use="atom:content/rz:logentry/rz:request/@tid"/>
    <xsl:template match="/">
                <xsl:apply-templates select="atom:feed" mode="tree"/>
    </xsl:template>
    <xsl:template match="atom:feed" mode="tree">
        <!-- Recurse into the feed and make data to load into the tree -->
        <log>
            <xsl:apply-templates select="atom:entry" mode="item"/>
            <!--<xsl:apply-templates select="atom:entry[atom:content/rz:logentry/rz:response/@tid]"
                mode="entry"/>-->
        </log>
    </xsl:template>
    <xsl:template match="atom:entry" mode="entry">
        <!-- The parent request is the one with a @tid on the response -->
        <entry entryid="{atom:id}" name="{atom:title}" elapsed="{atom:content/rz:logentry/@elapsed}">
            <xsl:variable name="thistid" select="atom:content/rz:logentry/rz:response/@tid"/>
            <!--<xsl:apply-templates select="key('getsubentry', $thistid)" mode="item"/>-->
        </entry>
    </xsl:template>
    <xsl:template match="atom:entry" mode="item">
        <item entryid="{atom:id}" name="{atom:title}" elapsed="{atom:content/rz:logentry/@elapsed}"/>
    </xsl:template>
</xsl:stylesheet>
