import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import aspose.pdf as ap
import collections
md_reports = pd.read_excel(r'C:\Users\a.banning\Downloads\23_24_Matchday-Reports.xlsx', sheet_name='MLS')

a = list(md_reports['Unnamed: 0'])

d = [item for item, count in collections.Counter(a).items() if count > 1]
idx_mdr = md_reports.index[md_reports['Unnamed: 1'] == 'Matchday Report'].tolist()
idx_mdr.pop(0) # Pop rehearsals
idx_md = md_reports.index[md_reports['Unnamed: 1'] == 'MD'].tolist()

rows = md_reports.iloc[idx_md]

# Regular Season
new_df = []
for i, idx in enumerate(idx_mdr):
    if i == 38:
        new_df.append(md_reports[idx + 6:])
        #new_df.append(md_reports[idx+6:idx_mdr[i+1]])
    else:
        #new_df.append(md_reports[idx+6:])
        new_df.append(md_reports[idx + 6:idx_mdr[i + 1]])
new_df.pop(26) # Pop ALL-Star Game

# PlayOffs
# new_df = []
# for i, idx in enumerate(idx_mdr):
#     if not i >= 6:
#         new_df.append(md_reports[idx+6:idx_mdr[i+1]])
#     else:
#        new_df.append(md_reports[idx+6:])

# LeaguesCup
# new_df = []
# for i, idx in enumerate(idx_mdr):
#     if not i >= 9:
#         new_df.append(md_reports[idx+6:idx_mdr[i+1]])


# Testing to get the wanted variables out of a single df to implement this in the following loop
test = new_df[-1]
n_mwpartials = len([x for x in test.iterrows() if x[1]['Unnamed: 7'] == 'partial'])
n_retrans = len([x for x in test.iterrows() if x[1]['Unnamed: 7'] == 'retransmission'])
n_norestr = len([x for x in test.iterrows() if x[1]['Unnamed: 7'] == 'no restrictions'])
n_partials = np.sum([value for value in test['Unnamed: 8'] if type(value) == int])
n_videorestr = len([x for x in test.iterrows() if x[1]['Unnamed: 15'] == 'restrictions'])
n_mdeadlines = len([x for x in test.iterrows() if x[1]['Unnamed: 14'] == 'missed'])
n_trackstops = len([x for x in test.iterrows() if x[1]['Unnamed: 7'] == 'tracking-stop'])
n_matches = len([value for value in test['Unnamed: 0'] if len(str(value)) <= 4 and type(value) != float])


season_df = pd.DataFrame(columns=["Matchday", "Num of Matches", "Matches without Restrictions",
                                  "Num of Matches w. Partials", "Num of Partials",
                                  "Num of Retransmissions", "Num of Tracking Stops", "Num of Video Restrictions",
                                  "Num of Missed Deadlines"])
for i, df in enumerate(new_df):

    md = i+1
    n_mwpartials = len([x for x in df.iterrows() if x[1]['Unnamed: 7'] == 'partial'])
    n_partials = np.sum([value for value in df['Unnamed: 8'] if type(value) == int])
    n_retrans = len([x for x in df.iterrows() if x[1]['Unnamed: 7'] == 'retransmission'])
    n_norestr = len([x for x in df.iterrows() if x[1]['Unnamed: 7'] == 'no restrictions'])
    n_videorestr = len([x for x in df.iterrows() if x[1]['Unnamed: 15'] == 'restrictions'])
    n_mdeadlines = len([x for x in df.iterrows() if x[1]['Unnamed: 14'] == 'missed'])
    n_trackstops = len([x for x in df.iterrows() if x[1]['Unnamed: 7'] == 'tracking-stop'])
    n_matches = len([value for value in df['Unnamed: 0'] if len(str(value)) <= 4 and type(value) != float])

    md_df = pd.DataFrame(
        {'Matchday': md, 'Num of Matches': n_matches, 'Matches without Restrictions': n_norestr,
         'Num of Matches w. Partials': n_mwpartials, 'Num of Partials': n_partials,
         'Num of Retransmissions': n_retrans, 'Num of Tracking Stops': n_trackstops,
         'Num of Video Restrictions': n_videorestr, 'Num of Missed Deadlines': n_mdeadlines}, index=[0]
    )

    season_df = pd.concat([season_df, md_df])

season_df.to_excel('MLS_RegularSeason.xlsx')

# Tests for plotting
retrans_mean = [np.round(np.mean(season_df['Num of Retransmissions']),2) for x in range(0,len(new_df))]
plt.figure(figsize=(12,7))
plt.bar(x=season_df['Matchday'],height=season_df['Num of Retransmissions'], width=0.6, color='r')
plt.plot(season_df['Matchday'],retrans_mean,c='g',lw=3)
plt.title('Number of Retransmissions per Matchday')
plt.xlabel('Matchday')
plt.ylabel('Num. of Retransmissions')
plt.xticks(np.arange(0, 39, step=1))
plt.show()
plt.savefig(fname='retrans_test.png',format='png')



# Tests to create a PDF
# Initialize document object
document = ap.Document()

# Add page
page = document.pages.add()

# Initialize textfragment object
text_fragment = ap.text.TextFragment('Hello World')

#Add image
document.pages[1].add_image(r'C:\Users\a.banning\PycharmProjects\Work_Tracab\test.png',
                            ap.Rectangle(1500, 500, -1000, 700, True), image_height=100,
                            image_width=100)

# Add text fragment to new page
#page.paragraphs.add(text_fragment)

# Save updated PDF
document.save("output.pdf")