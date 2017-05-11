#!/usr/bin/env ruby
# commify - format numbers with commas

# examples:
# 
# du -k . | sort -nr | commify.rb 
# 
# commify.rb 132461363141346432 6643145 1234

require 'optparse'

########################################
# FUNCTIONS
########################################

# from https://www.ruby-forum.com/topic/54123#32751
def commify(str)
  str.to_s.reverse.gsub(/(\d\d\d)(?=\d)(?!\d*\.)/,'\1,').reverse
end

def parse_args
  o = {}
  OptionParser.new do |opts|
    opts.banner = "Usage: commify.rb [options]"
    opts.on("-h", "--help", "Show help") do
     puts opts 
     exit
    end
    opts.on("-f", "--filter", "Run as filter") do 
      o[:filter] = true
    end
    opts.on("-a", "--all", "Commify all numbers") do 
      o[:replace_all] = true
    end
  end.parse!
  return o
end

def commify_line( line, replace_all=true )
  if replace_all
    line.gsub(/\d+/) { |n| commify(n) }
  else
    line.sub(/\d+/)  { |n| commify(n) }
  end
end

########################################
# MAIN BODY
########################################
opts = parse_args()

# by default, calling with ONLY numeric arguments will cause the arguments
# themselves to be commified. However, any non-numeric arguments (or --filter)
# will trigger filter mode, which causes the arguments to be treated as file
# names to be read and filtered. No filename also triggers filter mode

if opts[:filter] || ARGV.empty? || ARGV.any? { |s| s.match /\D/ }
  warn "Enter numbers" if ARGV.empty? and STDIN.tty?
  ARGF.each do |line|
    print commify_line(line, opts[:replace_all])
  end
else
  puts ARGV.map { |n| commify(n) }
end

