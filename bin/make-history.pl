#!/usr/bin/perl -w

# v2.2.1, dougmc@frenzied.us, 07/14/95

# User configurable varliables.
$history_master_file =  $ENV{'HOME'} . "/.history-master" ;
$history_recent_file =  $ENV{'HOME'} . "/.history-recent" ;
$history_lockfile    =  $ENV{'HOME'} . "/.history-lock" ;
$history_dir         =  $ENV{'HOME'} . "/.history" ;
$history_recent_lines = 1995 ;

# Ok, we'll keep in memory an associative array with history lines
# and order in list.
# the subscript will be the line - the value will be the order (kind of
# backwards, but kinda cool too.

# Initialization
umask 077 ;
chdir $history_dir || die "Can't cd to $history_dir - $!\n" ;
$current_line_number = 0 ;
undef %history_line ;
$total_lines_read = 0 ;
$total_unique_lines_read = 0 ;
$eof_marker = "=== End of old history ===" ;

$SIG{'INT'} = 'interrupt_handler';
$SIG{'TERM'} = 'interrupt_handler';
$SIG{'HUP'} = 'interrupt_handler';
&interrupt_handler if (0); # Just to suppress warning from perl -w.

@files = <*-history-*> ;
;# @files = `ls --sort=time -r *-history-* 2> /dev/null` ;

if (! @files) {
   print "No history to make in $history_dir ... exiting.\n" ;
   exit 0 ;
}

if (-f $history_lockfile) {
   die "Lockfile `$history_lockfile' already exists - aborting!\n" ;
}

open (TMP, "> $history_lockfile") || die "Can't open $history_lockfile - $!\n" ;
print TMP "$$\n" ;
close (TMP) || die "close failed: $!\n" ;
@delete_queue = (@delete_queue, $history_lockfile) ;

if (-f $history_master_file) {
   print "Reading in master history file $history_master_file ...\n" ;
   &read_in_history_file($history_master_file) ;
} else {
   print "Hmm ... no master history file.  No big deal - I'll make one.\n" ;
}

foreach $file (@files) {
   &read_in_history_file($file) ;
   @delete_queue = (@delete_queue, $file) ;
}

# Ok, the final line is going to be the EOF marker.
$history_line{$eof_marker} = $current_line_number ;
$current_line_number++ ;

$num_lines_that_arent_recent = ($total_unique_lines_read - $history_recent_lines) ;

print "Ok, done reading files.  Writing $total_unique_lines_read lines to master file ...\n" ;
print "                ... also writing $history_recent_lines lines to recent history file ...\n" ;


# Backup the history master file, just in case something goes boom.

if (-f $history_master_file) {
   $backup_master_file = join ("-", $history_master_file, "backup", $$) ;

   rename ($history_master_file, $backup_master_file) || 
      die "Could not make backup of $history_master_file - $! - aborting!\n" ;

   @delete_queue = (@delete_queue, $backup_master_file) ;
}

open(H, "> $history_master_file") ;
open(H2, "> $history_recent_file") ;

$number_of_lines_saved_master = 0 ;
$number_of_lines_saved_recent = 0 ;

foreach $line (sort by_order (keys %history_line)) {

   if ($history_line_comment{$line}) {
      print H "$history_line_comment{$line}\n" ;
   }
   print H "$line\n" ;
   $number_of_lines_saved_master++ ;
   $num_lines_that_arent_recent-- ;
   if ($num_lines_that_arent_recent < 0) {
      if ($history_line_comment{$line}) {
         print H2 "$history_line_comment{$line}\n" ;
      }
      print H2 "$line\n" ;
      $number_of_lines_saved_recent++ ;
   }
}
close (H) || die "close H: failed: $!\n" ;
close (H2) || die "close H2: failed: $!\n" ;
print "$number_of_lines_saved_master lines of history saved to $history_master_file\n" ;
print "$number_of_lines_saved_recent lines of history saved to $history_recent_file\n" ;

print "Cleaning up ...\n" ;
$cleaning_up = 1 ;
foreach $file (@delete_queue) {
    unlink $file || warn "can't unlink $file: $!\n" ;
}

# end of the program

# To make both perl 4 and perl 5 happy ...
$a = 0 ; $b = 0 ;
sub by_order {
   $history_line{$a} <=> $history_line{$b} ;
}

# This routine reads in each file.
sub read_in_history_file {

   local ($file_to_read, $lines_read, $unique_lines_read, $marker_found,
      $doing_master_file, $lines_skipped, $history_comment_line) ;

   $file_to_read = $_[0] ;

   $lines_read = 0 ;
   $unique_lines_read = 0 ;
   $lines_skipped = 0 ;

   $file_to_print = $file_to_read ;
   $file_to_print =~ s|.*/|| ;

   printf ("%25s : ", $file_to_print) ;

   # Ok, we read in the file until we find the `=== End of old history ==='
   # line, after which we include everything.  If we don't find it, we
   # reopen the file, and then include everything. 

   $marker_found = 0 ;

   # If the file that we're reading in is the master file, don't look for
   # the marker - we ignore it if it's there anyways.

   open (H, "< $file_to_read") || die "Can't open `$file_to_read'\n" ;

   if ($file_to_read eq $history_master_file) {
      $doing_master_file = 1 ;
   } else {
      $doing_master_file = 0 ;
   }

   if (! $doing_master_file) {
      while (<H>) {
	 chop ;

         next if /^#[+]/ ;   # Ignore those time lines, this time.

         $lines_skipped++ ;
         if (/^$eof_marker$/o) {
            $marker_found = 1 ;
            last ;
         }
      }
   }

   # If we didn't find it, close the file and reopen it.
   if (! $marker_found) {

   # a kludge - if we're doing the master file, don't report on an unfound marker.
      $marker_found = 1 if ($doing_master_file) ;

      close (H) ;
      open (H, "< $file_to_read") || die "Can't open `$file_to_read'\n" ;
      $lines_skipped = 0 ;
   }

   while (<H>) {

      chop ;

      # strip off leading and trailing spaces
      s/^\s+// ;
      s/\s+$// ;

      # Go ahead and save those time lines, if they're available.
      if (/^#[+]/) {
         $history_comment_line = $_ ;
         next ;
      }

      $lines_read++ ;

      # If this line has already been in our history file, it's automatically
      # moved.  This is pretty slick, I think ...

      if (! $history_line{$_}) {
	  $unique_lines_read++ ;
      }
      $history_line{$_} = $current_line_number ;
      if ($history_comment_line) {
	 $history_line_comment{$_} = $history_comment_line ;
         undef $history_comment_line ;
      } else {
	 undef $history_line_comment{$_} ;
      }
      $current_line_number++ ;

   }
   close (H) ;
   printf (" %4d skipped, %5d read, %5d saved", $lines_skipped, $lines_read, $unique_lines_read ) ;

   if (!$marker_found) {
      print " (no marker)" ;
   }
   print "\n" ;

   if (($lines_skipped > 5000) && ($lines_read < 1)) {
       warn "\n   Woah, this looks fishy ... is this a master file?!?!\n" ;
       warn "      pausing for 10s ... ^C to abort (cleanly)!\n" ;
       sleep 10 ;
   }

   $total_lines_read = $total_lines_read + $lines_read ;
   $total_unique_lines_read = $total_unique_lines_read + $unique_lines_read ;
}

sub interrupt_handler {
   local ($sig) = @_ ;

   if ($cleaning_up) {
       warn "caught a SIG$sig during cleanup - ignoring, finishing cleanup\n" ;
       return ;
   }

   print "\n" ;

   # At this point, we're gonna exit.  Might as well erase this ...
   unlink ($history_lockfile) ;

   if ($backup_master_file) {

      warn "caught a SIG$sig -- possible damage done!\n\n" ;
      warn "You probably need to restore the backup history-master file with this command :\n\n" ;
      warn "   mv $backup_master_file \\\n      $history_master_file\n\n" ;
      warn "The history-recent file is probably lost, but is easily recreated.\n\n" ;
   } else {
      warn "caught a SIG$sig -- aborting cleanly.\n" ;
   }
   exit 1 ;
}
