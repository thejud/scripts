#!/usr/bin/env ruby

require 'optparse'

########################################
# FUNCTIONS
########################################

def parse_args
  o = {cmd: 'strip'}
  OptionParser.new do |opts|
    opts.banner = "Usage: trim.rb [options]"
    opts.on("-h", "--help", "Show help") do
     puts opts 
     exit
    end
    opts.on("-r", '--rtrim', '--rstrip', "right trim") do
      o[:cmd] = 'rstrip'
    end
    opts.on("-l", '--ltrim', '--lstrip', "left trim") do
      o[:cmd] = 'lstrip'
    end
  end.parse!
  return o
end

########################################
# MAIN BODY
########################################
opts = parse_args()
ARGF.each { |line| puts line.send(opts[:cmd]) }
