package main

import (
    "bytes"
    "fmt"
    "./yencode"
    "hash/crc32"
    "strings"
    "time"
)

type Article struct {
    Body     []byte
    NzbData  NzbFile
    Segment  NzbSegment
    FileName string
}

type ArticleData struct {
    PartNum   int64
    PartTotal int64
    PartSize  int64
    PartBegin int64
    PartEnd   int64
    FileNum   int
    FileTotal int
    FileSize  int64
    FileName  string
}

func NewArticle(p []byte, data *ArticleData, subject string) *Article {
    buf := new(bytes.Buffer)
    buf.WriteString(fmt.Sprintf("From: %s\r\n", Config.Global.From))

    var groups string
    if len(*groupFlag) > 0 {
        groups = *groupFlag
    } else {
        groups = Config.Global.DefaultGroup
    }
    buf.WriteString(fmt.Sprintf("Newsgroups: %s\r\n", groups))

    var msgid string
    t := time.Now()
    msgid = fmt.Sprintf("%.5f$abook@abook", float64(t.UnixNano())/1.0e9)
    buf.WriteString(fmt.Sprintf("Message-ID: <%s>\r\n", msgid))
    buf.WriteString(fmt.Sprintf("X-Newsposter: ABook\r\n"))
    buf.WriteString(fmt.Sprintf("X-Abuse: ABUSE@usenet.byproxy.au\r\n"))
    buf.WriteString(fmt.Sprintf("X-Mail-Complaints-To: ABUSE@usenet.byproxy.au\r\n"))
    buf.WriteString(fmt.Sprintf("Mail-Complaints-To: ABUSE@usenet.byproxy.au\r\n"))
    buf.WriteString(fmt.Sprintf("X-Complaints-To: ABUSE@usenet.byproxy.au\r\n"))
    buf.WriteString(fmt.Sprintf("Organization: usenet.byproxy.au\r\n"))
    buf.WriteString(fmt.Sprintf("Injection-Info: usenet.byproxy.au; mail-complaints-to=\"ABUSE@usenet.byproxy.au\"\r\n"))

    // Build subject
    // spec: c1 [fnum/ftotal] - "filename" yEnc (pnum/ptotal)
    var subj string
    if len(Config.Global.SubjectPrefix) > 0 {
        subj = fmt.Sprintf("%s %s", Config.Global.SubjectPrefix, subject)
    } else {
        subj = subject
    }

    subj = fmt.Sprintf("%s [%d/%d] - \"%s\" yEnc (%d/%d)", subj, data.FileNum, data.FileTotal, data.FileName, data.PartNum, data.PartTotal)
    buf.WriteString(fmt.Sprintf("Subject: %s\r\n\r\n", subj))

    // yEnc begin line
    buf.WriteString(fmt.Sprintf("=ybegin part=%d total=%d line=128 size=%d name=%s\r\n", data.PartNum, data.PartTotal, data.FileSize, data.FileName))
    // yEnc part line
    buf.WriteString(fmt.Sprintf("=ypart begin=%d end=%d\r\n", data.PartBegin+1, data.PartEnd))

    //log.Debug("%+v", buf)
    // Encoded data
    yencode.Encode(p, buf)
    // yEnc end line
    h := crc32.NewIEEE()
    h.Write(p)
    buf.WriteString(fmt.Sprintf("=yend size=%d part=%d pcrc32=%08X\r\n", data.PartSize, data.PartNum, h.Sum32()))
    // Nzb
    n := NzbFile{
        Groups:  strings.Split(groups, ","),
        Poster:  Config.Global.From,
        Date:    t.Unix(),
        Subject: subj,
    }
    s := NzbSegment{
        Bytes:     data.PartSize,
        Number:    data.PartNum,
        MessageId: msgid,
    }
    return &Article{Body: buf.Bytes(), NzbData: n, Segment: s, FileName: data.FileName}
}
