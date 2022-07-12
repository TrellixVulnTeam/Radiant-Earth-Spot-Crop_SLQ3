# import the needed modules
import pandas as pd
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
from collections import Counter
import warnings
warnings.filterwarnings("ignore")

# import own modules 
if __name__ != "__main__":
    from src.train_test_function import train_test_split_fields


class ResamplingProcess():
    """ Class to resample the crop types.
    """
    def __init__(self, ROOT_DIR:str) -> None:
        # set the directory and the chunks in which the larger fields are splitted 
        self.ROOT_DIR = ROOT_DIR
        self.DATA_DIR = f"{self.ROOT_DIR}/data"

    def load_data(self):
        # load the data
        self.df = pd.read_csv(f"{self.DATA_DIR}/data_after_FE.csv")

    def do_train_test_split(self):
        # do the train-test split
        self.df_train, self.df_test = train_test_split_fields(self.df, 0.7)

    def merge_crop_types(self):
        # create a copy dataset with only 8 classes instead of 9 (8 and 9 were combined together in one class)
        self.df_label_comb= self.df_train.copy()
        self.df_label_comb
        self.df_label_comb["label"].replace({9:8}, inplace=True)

    def oversampling(self):
        """ Oversamples the underrepresented crop classes.
        """
        # use the new dataset to define the desired sample size
        self.n_class_1 = self.df_label_comb[self.df_label_comb.label==1].shape[0]
        self.class_1 = self.df_label_comb[self.df_label_comb.label==1]
        # from the new dataset  create the subset of classes i want to oversample
        df_over = self.df_label_comb.loc[self.df_label_comb['label'].isin([5,6,3,8])]
        #from our subset define the target and features
        X_over= df_over.drop('label',axis=1)
        y_over = df_over['label']
        # oversample the X_under and y_under
        strategy = { 8:self.n_class_1, 3:self.n_class_1, 5:self.n_class_1, 6:self.n_class_1}
        over = RandomOverSampler(sampling_strategy=strategy)
        X_overS, y_overS = over.fit_resample(X_over, y_over)
        print(f"overSampling: {Counter(y_overS)}")
        # create a set of oversampled data by merging the above sampled feature and Target
        self.df_overS = pd.concat([X_overS,y_overS],axis= 1)

    def undersampling(self):
        """ Undersamples the overrepresented crop classes.
        """
        # repeat the same thing for undersampling
        df_under = self.df_label_comb.loc[self.df_label_comb['label'].isin([4,2,7])]
        X_under= df_under.drop('label',axis=1)
        y_under = df_under['label']
        strategy = {4:self.n_class_1,2:self.n_class_1,7:self.n_class_1}
        under = RandomUnderSampler(sampling_strategy=strategy)
        X_underS, y_underS = under.fit_resample(X_under, y_under)
        print(f"underSampling: {Counter(y_underS)}")
        self.df_underS = pd.concat([X_underS,y_underS],axis= 1)

    def save_train_test_data(self):
        # create a balanced dataset by merging the 3 subsset we created above
        df_class1= pd.concat([self.df_overS, self.df_underS, self.class_1],axis=0)
        # save the resample data set as csv file 
        df_class1.to_csv(f'{self.DATA_DIR}/Train_Dataset4.csv',index=False) # create a csv file
        self.df_test.to_csv(f'{self.DATA_DIR}/Test_Dataset.csv',index=False)
        print(f"Save the train and test data to {self.DATA_DIR}")
    
    def start_resampling(self):
        """ Run the resampling process and create a data set
            usable for training the model.
        """
        self.load_data()
        self.do_train_test_split()
        self.merge_crop_types()
        self.oversampling()
        self.undersampling()
        self.save_train_test_data()
     

if __name__ == "__main__":
    from find_repo_root import get_repo_root
    from train_test_function import train_test_split_fields
    ROOT_DIR = get_repo_root()

    resampling = ResamplingProcess(ROOT_DIR=ROOT_DIR)
    resampling.start_resampling()
   
