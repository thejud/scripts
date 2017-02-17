#!/usr/bin/env ruby
# re-format an initial date field in a line for easier analysis
#
# echo "2017-02-01T10:42:17+0000 some msg" | datesplit.rb
#   2017 02 01 10 42 17 +0000 some msg
#
# Use in conjunction with datamash for easier time-based filtering and analysis, e.g. to
# generate a breakdown of ERROR by day and hour for entries after a specific time:
#
#   fgrep ERROR logfile | datesplit.rb --after '2017-01-02T15:00:00' | datamash -W -s -g 3,4 -c 10

require 'date'
require 'logger'
require 'optparse'


########################################
# FUNCTIONS
########################################

def parse_args
  o = {}
  OptionParser.new do |opts|
    opts.banner = "Usage: #{File.basename(__FILE__)} [options]"
    opts.on("-h", "--help", "Show help") do
     puts opts
     exit
    end
    opts.on('-d', '--date', 'Keep the date, e.g. fields 1-3') do
      o[:date] = true
    end
    opts.on('-f', '--fields F1,F2...', Array, 'fields(s) to include, 1 is first, max 7') do |v|
      o[:fields] ||= []
      o[:fields] += v.map { |f| f.to_i}.reject { |f| f > 7 }
    end
    opts.on('-a', '--after DateTime', 'Only dates >= DateTime') do |v|
      o[:after] = DateTime.parse(v)
    end
    opts.on('-b', '--before DateTime', 'Only dates =< DateTime') do |v|
      o[:before] = DateTime.parse(v)
    end
    opts.on('-s', '--skip COUNT', Integer, 'Skip to line COUNT in the file. 1 is frst') do |v|
      o[:skip_count] = v - 1
    end
  end.parse!
  return o
end


def main
  opts = parse_args
  log=Logger.new STDERR
  skip = !!(opts[:after] or opts[:before])
  log.info { "skipping #{opts[:skip_count]} line(s)" } if opts[:skip_count]
  ARGF.each_with_index do |line, i|
    next if (opts[:skip_count] and i < opts[:skip_count] )
    /^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\S*))\s/.match(line) do |m|
      d = DateTime.parse(m[1]) rescue nil
      if d
        # filter by date if we've found one.
        case
        when (opts[:after] && opts[:before])
          skip = (d < opts[:after] ) || (d > opts[:before] )
        when opts[:after]
          skip = (d < opts[:after])
        when opts[:before]
          skip = d > opts[:before]
        end
        fmt = case
              when opts[:date]
                '%Y %m %d'
              when opts[:fields]
                fvals = %W{%a %Y %m %d %H %M %S %z}  # %a for weekday
                opts[:fields].map { |f| fvals[f] }.join(" ")
              else
                '%Y %m %d %H %M %S %z'
              end
        line.sub!(m[1], d.strftime(fmt))
      end
    end
    print line unless skip
  end
end

########################################
# MAIN BODY
########################################

if __FILE__ == $0    # this script can be required as a library
  main
end
