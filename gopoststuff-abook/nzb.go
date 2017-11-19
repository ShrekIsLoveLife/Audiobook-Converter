package main

import (
	"encoding/xml"
	"io/ioutil"
	"regexp"
	"strings"
	"sort"
)

const (
	NzbHeader = `<?xml version="1.0" encoding="UTF-8"?>` + "\n"
	NzbDoctype = `<!DOCTYPE nzb PUBLIC "-//newzBin//DTD NZB 1.1//EN" "http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd">` + "\n"
)

type NzbFiles []NzbFile

func (s NzbFiles) Len() int           { return len(s) }
func (s NzbFiles) Less(i, j int) bool { return s[i].Subject < s[j].Subject }
func (s NzbFiles) Swap(i, j int)      { s[i], s[j] = s[j], s[i] }

type NzbSegments []NzbSegment

func (s NzbSegments) Len() int           { return len(s) }
func (s NzbSegments) Less(i, j int) bool { return s[i].Number < s[j].Number }
func (s NzbSegments) Swap(i, j int)      { s[i], s[j] = s[j], s[i] }

type Nzb struct {
	XMLName xml.Name  `xml:"nzb"`
	XMLns   string    `xml:"xmlns,attr"`
	Head    []Meta    `xml:"head>meta"`
	File    NzbFiles  `xml:"file"`
}

type Meta struct {
	Type  string `xml:"type,attr"`
	Value string `xml:",innerxml"`
}

type NzbFile struct {
	Poster   string       `xml:"poster,attr"`
	Date     int64        `xml:"date,attr"`
	Subject  string       `xml:"subject,attr"`
	Groups   []string     `xml:"groups>group"`
	Segments NzbSegments  `xml:"segments>segment"`
}

type NzbSegment struct {
	XMLName   xml.Name `xml:"segment"`
	Bytes     int64    `xml:"bytes,attr"`
	Number    int64    `xml:"number,attr"`
	MessageId string   `xml:",innerxml"`
}

func CreateNzb(filename string, nzb *Nzb) error {
	sort.Sort(nzb.File)
	for i, _ := range nzb.File {
		sort.Sort(nzb.File[i].Segments)
	}
	nzb.XMLns = "http://www.newzbin.com/DTD/2003/nzb"
	if output, err := xml.MarshalIndent(nzb, "", "    "); err == nil {
		output = []byte(NzbHeader + NzbDoctype + string(output))
		err := ioutil.WriteFile(filename, output, 0755)
		if err != nil {
			return err
		}
	}
	return nil
}

func SafeFileName(str string) string {
	name := strings.ToLower(str)
	//name = path.Clean(path.Base(name))
	name = strings.Trim(name, " ")
	separators, err := regexp.Compile(`[ &_=+:]`)
	if err == nil {
		name = separators.ReplaceAllString(name, "-")
	}
	legal, err := regexp.Compile(`[^[:alnum:]-.]|-yenc-\d*.+`)
	if err == nil {
		name = legal.ReplaceAllString(name, "")
	}
	for strings.Contains(name, "--") {
		name = strings.Replace(name, "--", "-", -1)
	}
	return name
}
