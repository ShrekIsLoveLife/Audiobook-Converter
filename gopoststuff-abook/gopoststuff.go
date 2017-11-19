package main

import (
	"gopkg.in/gcfg.v1"
	"flag"
	"fmt"
	"gopkg.in/op/go-logging.v1"
	"os"
	"os/user"
	"path/filepath"
	"runtime"
	"runtime/pprof"
)

const (
	GPS_VERSION = "0.3.3-abook"
)

// Command ling flags
var configFlag = flag.String("c", "", "Use alternative config file")
var dirSubjectFlag = flag.Bool("d", false, "Use directory names as subjects")
var groupFlag = flag.String("g", "", "Newsgroup(s) to post to - separate multiple with a comma \",\"")
var subjectFlag = flag.String("s", "", "Subject to use")
var verboseFlag = flag.Bool("v", false, "Show verbose debug information")
var cpuProfileFlag = flag.String("cpuprofile", "", "Write CPU profiling information to FILE")
var allCpuFlag = flag.Bool("allcpus", false, "Use all CPUs for stuff [ALPHA]")
var versionFlag = flag.Bool("version", false, "prints current version")
var nzbFlag = flag.String("nzb", "", "Nzb filename")
var nzbMetaPass = flag.String("rarpw", "", "Add password for rar archives to nzb head.")
var serverFlag = flag.String("server", "", "Use specified server to post.")

// Logger
var log = logging.MustGetLogger("gopoststuff-abook")

// Config
var Config struct {
	Global ConfigGlobal
	Server map[string]*ConfigServer
}

type ConfigGlobal struct {
	From          string
	DefaultGroup  string
	SubjectPrefix string
	DefaultNzb    string
	DefaultServer string
	ArticleSize   int64
	ChunkSize     int64
}

type ConfigServer struct {
	Address     string
	Port        int
	Username    string
	Password    string
	Connections int
	TLS         bool
	InsecureSSL bool
}

func main() {
	// Use our own Usage function to print version number
	flag.Usage = func() {
		fmt.Println("Version: ", GPS_VERSION)
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		flag.PrintDefaults()
	}

	// Parse command line flags
	flag.Parse()

	// Check for version argument
	if *versionFlag {
		fmt.Println("Version: ", GPS_VERSION)
		os.Exit(0)
	}

	var format = logging.MustStringFormatter(" %{level: -8s} %{message}")
	// Set up logging
	if *verboseFlag {
		format = logging.MustStringFormatter(" %{level: -8s} %{shortfile} %{message}")
		logging.SetLevel(logging.DEBUG, "gopoststuff")
	} else {
		logging.SetLevel(logging.INFO, "gopoststuff")
	}
	logging.SetFormatter(format)

	log.Info("gopoststuff starting...")

	// Make sure -d or -s was specified
	if len(*subjectFlag) == 0 && !*dirSubjectFlag {
		log.Fatal("Need to specify -d or -s option, try gopoststuff --help")
	}

	// Check arguments
	if len(flag.Args()) == 0 {
		log.Fatal("No filenames provided")
	}

	// Check that all supplied arguments exist
	for _, arg := range flag.Args() {
		st, err := os.Stat(arg)
		if err != nil {
			log.Fatalf("stat %s: %s", arg, err)
		}

		// If -d was specified, make sure that it's a directory
		if *dirSubjectFlag && !st.IsDir() {
			log.Fatalf("-d option used but not a directory: %s", arg)
		}
	}

	var cfgFile string
	// Load config file
	if len(*configFlag) > 0 {
		cfgFile = *configFlag
	} else {
		// Default to user homedir for config file
		u, err := user.Current()
		if err != nil {
			log.Fatal(err)
		}
		cfgFile = filepath.Join(u.HomeDir, ".gopoststuff.conf")
	}

	log.Debug("Reading config from %s", cfgFile)

	err := gcfg.ReadFileInto(&Config, cfgFile)
	if err != nil {
		log.Fatal(err)
	}

	// Fix default values
	if Config.Global.ChunkSize == 0 {
		Config.Global.ChunkSize = 10240
	}

	// Maybe set GOMAXPROCS
	if *allCpuFlag {
		runtime.GOMAXPROCS(runtime.NumCPU())
	}
	log.Info("Using %d/%d CPUs", runtime.GOMAXPROCS(0), runtime.NumCPU())

	// Set up CPU profiling
	if *cpuProfileFlag != "" {
		f, err := os.Create(*cpuProfileFlag)
		if err != nil {
			log.Fatal(err)
		}

		pprof.StartCPUProfile(f)
		defer pprof.StopCPUProfile()
	}

	// Start the magical spawner
	Spawner(flag.Args())

	if *cpuProfileFlag != "" {
		log.Info("CPU profiling data saved to %s", *cpuProfileFlag)
	}
}
