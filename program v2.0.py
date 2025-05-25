from bs4 import BeautifulSoup
import pandas as pd
import re
import os

def main():
    raw_fp = ''
    raw_op = ''
    action = 2

    while action in [1,2]:
        print('\n=================================')

        # input folders
        print()
        print('INPUT FOLDER PATH where asa ang nakabutang all xml files')
        print('Protip: shift+click the input folder and click "copy as path" then paste here.')
        raw_fp = input('ENTER HERE: ')

        while not (os.path.exists(raw_fp.strip("\"")) and os.path.isdir(raw_fp.strip("\""))):
            print("\nERROR: This input folder does not exist or is not a folder! Try again!")
            raw_fp = input('ENTER HERE: ')

        if action == 2:
            print()
            print('OUTPUT FOLDER PATH where u want to save the csv files')
            print('Protip: shift+click the output folder and click "copy as path" then paste here.')
            raw_op = input('ENTER HERE: ')

            while not (os.path.exists(raw_op.strip("\"")) and os.path.isdir(raw_op.strip("\""))):
                print("\nERROR: This output folder does not exist or is not a folder! Try again!")
                raw_op = input('ENTER HERE: ')

        # program proper
        folder_path = raw_fp.strip("\"") # name sa folder where nakastore tanan xml file data
        output_folder = raw_op.strip("\"") # name sa folder where to put all output, csv files
        final_list = []

        for filename in os.listdir(folder_path):
            # open file
            f = open(f'{folder_path}/{filename}')

            # read file
            file = f.read()
            soup = BeautifulSoup(file, 'xml')

            # get temp
            temp_raw = soup.find("TEMPERATURE")
            try:
                temp = (float(temp_raw.text))/100
            except:
                temp = 'No Temp in XML'

            # get date n' time
            datetime_raw = soup.find("WavFileHandler", {"SamplingStartTimeLocal" : True})
            try:
                datetime_string = datetime_raw["SamplingStartTimeLocal"].split("T")
                date = datetime_string[0]
                time = datetime_string[1]
            except:
                date = 'No Date in XML'
                time = 'No Time in XML'

            if temp=='No Temp in XML' and date=='No Date in XML' and time=='No Time in XML':
                continue

            # get date n' time sa filename
            try:
                filename_date = re.search('\.(.+?)\.log', filename).group(1)
            except:
                filename_date = 'n/a'


            # keep results in final list
            temp_list = [filename, filename_date, temp, date, time]
            final_list.append(temp_list)

        df = pd.DataFrame(final_list, columns=['FILENAME', 'FILENAME_DATETIME', 'TEMPERATURE', 'SAMPLE_START_DATE', 'SAMPLE_START_TIME'])
        extract_foldername = folder_path.split('\\')[-1]

        new_filename = f'{output_folder}\{extract_foldername}.csv'

        while os.path.isfile(new_filename):
            print(f'\nWARNING: Filename "{extract_foldername}" already exist. Please provide another filename.\nCheck \"{output_folder}\" now.')
            newer_filename = input('ENTER NEW FILENAME HERE:')
            new_filename = f'{output_folder}\{newer_filename}.csv'

        print(f'\nSucessful.\nCheck \"{output_folder}\" now.')
        df.to_csv(new_filename, index=False)

        print()
        print('next action:')
        print('[1] new input folder. same output folder.')
        print('[2] new input folder. new output folder.')
        print('[3] exit')
        action = int(input('ENTER ACTION: '))

        if action not in [1,2,3]:
            print('ERROR: Invalid choice. Try again!')
            action = input('ENTER ACTION: ')

main()