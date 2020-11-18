import os, random, shutil

def prepare_labelling_data(report_folder, destination_file = 'reports_for_labelling.txt', num_files=100):

    filelist = os.listdir(report_folder)
    random.shuffle(filelist)
    file_count = 0
    with open(destination_file,'w') as lf: 
        for random_file in filelist:
            source_file=f'{report_folder}/{random_file}'
            try:
                with open(source_file,'r') as testfile:
                    txt = testfile.read()
                    txt.encode('latin-1')
                    lf.write(txt+'\n')
                file_count+=1
            except Exception as e:

                print(f'{source_file} is in different language')
                continue
        
            if file_count > num_files:
                break 

    print(f'Output written to {destination_file}')



def post_process_results(df, report_path, min_lat=8.4, max_lat=37.6, min_long=68.7, max_long= 98.25,
                        drop_empty_issues=True):
    
    #checking if text file exist
    file_exist = []
    for filename in df.filename:
        try:
            with open(report_path+filename, 'r') as report:
                _ = report.read()
                file_exist.append(True)
        except:
            file_exist.append(False)
    df['file_exist'] = file_exist
    valid_lats = []
    valid_longs = []

    #checking if lat long are in bounds
    for check_lat in df.lat:
        if check_lat >= min_lat and check_lat <= max_lat:
            valid_lats.append(True)
        else:
            valid_lats.append(False)

    for  check_long in df.long:
        if check_long >= min_long and check_long <= max_long:
            valid_longs.append(True)
        else:
            valid_longs.append(False)
    df['valid_latitude_value'] = valid_lats
    df['valid_longitude_value'] = valid_longs   
    df['valid_location'] = df['valid_latitude_value'] & df['valid_longitude_value'] 
    df =  df[df.file_exist & df.valid_location]
    df.drop(['valid_latitude_value','valid_longitude_value','valid_location','file_exist'], axis=1, inplace = True)

    #Dropping entries with empty issues
    if  drop_empty_issues:
        df = df[df.Issue.apply(len)!=0]
    df.reset_index(drop=True, inplace=True)
    for column in df.columns:
        if isinstance(df[column].iloc[0], list):
            df[column] = df[column].apply(lambda x: ', '.join(x))
    return df