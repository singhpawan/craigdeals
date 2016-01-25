import os
import sys
from  scraper import Scraper
from  time import sleep

def main():
  scp = Scraper('sfbay')
  scp.scrape(2500)
  scp.save('create')


if __name__ == '__main__':
  main()


