#!/bin/bash
# tscarter 6/14/2016
# version 2 teainswo 8/10/2016
# Plugged.sh - This routine looks at the full status of the tapes in a library
# It gets a list of all the libraries and has the user select which library to look through
# Then ejects qualified tapes if desired.
#
# V2.1 Buggered up by tscarter for scratch counts
# v2.2 Added section for determining locked tapes (Stolen mostly from Glenn Clayton)
# v2.3 6/28/2017 Added grouping for scratch tape. Counted vacant slots. added exception list lookup
# v2.4 8/20/2019 Added logging of vaulted tapes.

######################## get_lib ########################
function init {
  echo "Plugged.sh v2.4"
  exception_list=/home/tscarter/dont_vault_these_tapes  # This is the list of tapes NOT to vault
  if [ ! -f $exception_list ]
  then
    echo "Creating recall exception file"
    > $exception_list
  fi

  vault_candidates=0
}

######################## get_lib ########################
function get_lib {
# Get the library names
  if [ "$(obtool lsd -m | grep library | wc -l)" -gt "1" ]
  then
    echo "Active Libraries:"
    obtool lsd -m | grep library | awk '{print $2}'       # Print out the active libraries
    read -p "Select a library: " LIBRARY
    echo "You chose:" $LIBRARY
    echo
  else
    LIBRARY=$(obtool lsd -m | grep library | awk '{print $2}')
    echo "You chose:" $LIBRARY
  fi
}

######################## get_lsv ########################

###### This function gets us our raw data #####

function get_lsv {
  read -p "Do you want to load new catalog information? (y/n)" cataloginput
  if [[ $cataloginput =~ ^([yY][eE][sS]|[yY])$ ]]
  then
    echo "Getting volume data from catalog"
    obtool lsv -H -a > /tmp/catalog.tmp           ## This is all tapes seen by host
  fi
  echo "Getting volume data from library" $LIBRARY
#  obtool lsv -L $LIBRARY |grep -v Inventory > /tmp/lib.tmp      ## These are the current tapes in library
  obtool lsv -l -L $LIBRARY |grep -v Inventory > /tmp/longlib.tmp      ## These are the current tapes in library
  cat /tmp/longlib.tmp | grep -v vacant > /tmp/lib.tmp
}

######################## read_file ########################

#### this function gets us our list of tapes that should be ejected. ####

function read_file {
> /tmp/ejectlist.tmp
vault_candidates=0                                              # Clear vault candidate count
echo
echo "*** The following tapes appear to have missed being vaulted ***"
echo "*** They are closed, not Logarch, and not scratch           ***"

while read line
do
  id=$(echo $line | awk -F 'barcode' '{print $2}' | awk -F, '{print $1}')

  tpstatus=$(cat /tmp/catalog.tmp | grep $id | grep closed | grep -v Logarch | grep -v expired | grep -v deleted)
  ejectlist=$(echo $tpstatus | awk '{print $5}')

  if [ -n "$tpstatus" ]
  then                                                          # This is a candidate tape to vault
    if [ -z $(grep $id $exception_list) ]                       # String length is not 0
    then                                                        # found in vault exception list
      echo $tpstatus
      echo $ejectlist >> /tmp/ejectlist.tmp
      let vault_candidates=$vault_candidates+1
    else
      echo $id " found on vault exception list"
    fi                                                          # if found in vault exception list
  fi                                                            # if candidate to vault
done < /tmp/lib.tmp

}

######################## Vault ########################

### This function asks if the list of tapes should be ejected. ###

function vault {
  if [ "$vault_candidates" -gt "0" ]
  then
    read -p "Would you like to vault these $vault_candidates tapes NOW? (y/n)" ejinput
    if [[ $ejinput =~ ^([yY][eE][sS]|[yY])$ ]]
    then
      while read line
      do
        echo "obtool exportvol -L $LIBRARY -b $line"
        response=$(obtool exportvol -L $LIBRARY -b $line 2>&1)  # Capture the output in response
        echo $response                                          # Echo the response to the screen
        if [ -z "$response" ]                                   # Is there an error from obtool?
        then                                                    # If not, log a good vault
          echo "Success: obtool exportvol -L $LIBRARY -b $line" >> /usr/local/ops/osb/log/PLUGGED.vault.$(date +%Y%m%d).log
        fi
      done < /tmp/ejectlist.tmp
    fi
  else
    echo "Nothing to vault"
  fi
  echo
}

######################## WriteProtected ########################

### This function checks for write protected tapes
function writeprotected {
  > /tmp/ejectlist.tmp                                                  # Clear out eject list
  vault_candidates=0                                                    # Clear vault candidate count
#  (( linecount = 0 ))                                                  # Clear linecount
#  uselisttmp1=$(obtool lsd -l $LIBRARY | grep Use | grep -v all | sort -u | sed -e 's/^[^0-9]*//' -e 's/-/../g' -e 's/,/} {/g' -e 's/^/{/' -e 's/$/}/')
  uselisttmp1=$(obtool lsd -l $LIBRARY | grep Use | grep -v all | sort | sed -e 's/^[^0-9]*//' -e 's/-/../g' -e 's/,/} {/g' -e 's/^/{/' -e 's/$/}/')
# origional line        -     "Use list:               1-6,8-43,45-50,52-64,66-71,73-78,80,82-218"
# -e 's/^[^0-9]*//'     - Gets rid of everything not neumeric eg: "1-6,8-43,45-50,52-64,66-71,73-78,80,82-218"
# -e 's/-/../g'         - Changes - to .. Eg: "1..6,8..43,45..50,52..64,66..71,73..78,80,82..218"
# -e 's/,/} {/g'        - Puts braces where commas were Eg: "1..6} {8..43} {45..50} {52..64} {66..71} {73..78} {80} {82..218"
#-e 's/^/{/'            - Puts the first brace in Eg: "{1..6} {8..43} {45..50} {52..64} {66..71} {73..78} {80} {82..218"
# -e 's/$/}/'           - Puts the end brace in Eg: "{1..6} {8..43} {45..50} {52..64} {66..71} {73..78} {80} {82..218}"
                                                # Gives groups of uselist like {1..6} {8..43} {45..50} {52..64} {66..71} {73..78} {80} {82..218}
  if [[ -z ${uselisttmp1} ]] ; then
    echo Drives for $LIBRARY have all slots usable
  else
    slotcount=$(cat /tmp/longlib.tmp | grep -B 1 -m 1 -E iee[0-9]+: | sed -ne '1s/^.*in  *\([0-9][0-9]*\):.*$/\1/p')    # Gets the last slot number
    echo
    echo "------------------------------------------------------------------------------------"
    echo "Checking for Tapes excluded from Drive uselist for library $LIBRARY"
    echo "This should help identify broken / write protected tapes"

    for (( slotno=1; slotno<=${slotcount}; slotno++ ))                  # Create uselist array and set to 0
    do
      uselist[${slotno}]=0
    done

    while read input_line                                               # Read through the uselists. Put in array
    do
      uselisttmp2=$(echo "$input_line"| sed -e 's/{\([0-9]\{1,4\}\)}/\1/g') # combines multiple lines in uselist1 into one line
      slotsforuse=$(eval echo $uselisttmp2)    # creates list like 1 2 3 4 5 6 8 dropping any slots that any drive might not use. (7 is missing)

      for slotno in $slotsforuse                                        # increment array for each entry
      do
        (( uselist[$slotno]++ ))
      done
    done <<< $uselisttmp1

    echo
    echo "*** The following tapes appear to be write protected or have hardware issues.***"
    echo "*** They are not used by at least 3 drives. They are scratch                 ***"


    for slotno in ${!uselist[@]}                                        # Read through slots.
    do
      if (( ${uselist[$slotno]} <= 3 ))                                 # Look for 3 or more drives that can't use this slot
      then
#        echo "set on $slotno"
#        grep " $slotno:" /tmp/longlib.tmp
        id=$(grep " $slotno:" /tmp/longlib.tmp |  awk -F 'barcode' '{print $2}' | awk -F, '{print $1}') # Get the barcode of the tape in that slot
#        echo "id: $id"
        tpstatus=$(cat /tmp/catalog.tmp | grep $id | egrep "expired|deleted" )  # Should be a scratch tape. Should be able to be written to
        echo $tpstatus
        echo $id >> /tmp/ejectlist.tmp
        let vault_candidates=$vault_candidates+1
      fi
    done
  fi
}

######################## scratch ########################
function scratch {
  open=0
  closed=0
  total=0
  scratch=0
  expired=0
  deleted=0
  unknown=0
  echo
  echo "-------------------------------------------------"
  echo "*** status of all of the tapes in the library ***"

  while read line
  do
    let total=$total+1
    id=$(echo $line | awk -F 'barcode' '{print $2}' | awk -F, '{print $1}')
    tpstatus=$(cat /tmp/catalog.tmp | grep $id )
#   tpstatus=$(cat /tmp/catalog.tmp | grep $id | grep -v closed)
    echo -n "$id $tpstatus"

    if [ -z "$tpstatus" ]
    then
      echo " ---scratch"
      let scratch=$scratch+1
    elif [ -n "$(echo $tpstatus | grep expired )" ]
    then
      echo " ---expired"
      let expired=$expired+1
    elif [ -n "$(echo $tpstatus | grep deleted )" ]
    then
      echo " ---deleted"
      let deleted=$deleted+1
    elif [ -n "$(echo $tpstatus | grep closed )" ]
    then
      echo " ---closed"
      let closed=$closed+1
    elif [ -n "$(echo $tpstatus | grep open )" ]
    then
      echo " ---open"
      let open=$open+1
    else
      echo " ---unknown"
      let unknown=$unknown+1
    fi

  done < /tmp/lib.tmp

  empty=$(grep vacant /tmp/longlib.tmp | grep -v iee | grep -v dte | wc -l)
  total_scratch=$(( $scratch + $expired + $deleted ))

  echo
  echo "---------------------Totals---------------------------------"
  echo "  Raw Scratch $scratch"
  echo "  Expired $expired"
  echo "  Content Deleted $deleted"
  echo "Total Scratch $total_scratch"
  echo
  echo "Empty Slots $empty"
  echo
  echo "Open $open"
  echo "Closed $closed"
  echo "Unknown $unknown"
  echo "Total tapes $total"

}

######################## Main ###########################
init
get_lib
get_lsv
read_file
vault
writeprotected
vault
scratch

#end plugged.sh
