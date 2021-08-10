#!/usr/bin/env bash

round_down_positive_float(){
  # Caveats:
  # * This function only works for floats with xyz.abc notation.
  # * Scientific notation requires other approaches.
  # * negative floats will be rounded up
  the_float="$1"
  LC_ALL=C echo "${the_float%.*}"
}
