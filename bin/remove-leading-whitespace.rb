#!/usr/bin/env ruby
# trim leading whitespace from a string, determined by first line
# useful for text copied from screen/formatting

spaces_to_remove = nil
ARGF.each_line do |line|
  unless spaces_to_remove
    /^(\s)+/.match(line) do |m|
      spaces_to_remove = m[0].size
    end
  end
  print line[spaces_to_remove..-1]
end

