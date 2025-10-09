
#fromRCVcurn paser

def dominion5_10_messy(cvr_path: Union[str, pathlib.Path], office: str) -> Dict[str, List]:
    """
    Reads ballot data from Dominion V5.10 CVRs for a single contest.

    Files expected in cvr_path:
        - ContestManifest.json
        - CandidateManifest.json
        - PrecinctPortionManifest.json
        - (optional) PrecinctManifest.json
        - DistrictManifest.json
        - DistrictTypeManifest.json
        - DistrictPrecinctPortionManifest.json
        - BallotTypeManifest.json
        - CountingGroupManifest.json
        - BallotTypeContestManifest.json
        - TabulatorManifest.json
        - CvrExport*.json (multiple possible)

    :param cvr_path: Path where CVR files are located.
    :type cvr_path: Union[str, pathlib.Path]
    :param office: Names which contest's ballots should be read. Must match a contest name in ContestManifest.json.
    :type office: str
    :raises RuntimeError: If ballotIDs pulled from ImageMask field are not unique. Or if regex used to pull ballotID from ImageMask field malfunctions.
    :return: A dictionary of lists containing informtion in the CVR file. Ranks are combined into per-ballot lists and stored with the key 'ranks'. A 'weight' key and list of 1's is added to the dictionary if no 'weight' column exists. All weights are of type :class:`decimal.Decimal`.
    :rtype: Dict[str, List]
    """
    detailedOvervote=True

    total_cards = 0

    if detailedOvervote == True:
        overvotelist=[]
        outstackconditionalnumber=0
        falsevotenumber=0
        NotFalseis7=0
        AmbigiousCount=0
        saved_outstack_ids = set()
        saved_7card_ids = set()
        saved_7ballottype = set()
        saved_7precinctportion={}
        saved_7countinggroup={}
        allcountinggroup={}
        saved_7Record={}
        saved_7Batch={}
        saved_7Tabulator={}
        printedballotyet=10
        C1Count=0
        C2Count=0
        C3Count=0
        C3_1Count=0
        C4Count=0

        O0Count=0
        O1Count=0
        O2Count=0
        O5Count=0
        O4Count=0
        O6Count=0
        O9Count=0
        O10Count=0
        O11Count=0
        O12Count=0
        O13Count=0
        O14Count=0
        cards_with_outstack_7 = 0  # Counter for cards with OutstackConditionId 7

        lowmarkunambigiouscount=0

    path = pathlib.Path(cvr_path)
    #print(path)
    # load manifests, with ids as keys
    with open(path / "ContestManifest.json", encoding="utf8") as f:
        for i in json.load(f)["List"]:
            if i["Description"].strip() == office:
                current_contest_id = i["Id"]
                current_contest_rank_limit = i["NumOfRanks"]

    candidate_manifest = {}
    with open(path / "CandidateManifest.json", encoding="utf8") as f:
        for i in json.load(f)["List"]:
            candidate_manifest[i["Id"]] = i["Description"]

    precinctPortion_manifest = {}
    with open(path / "PrecinctPortionManifest.json", encoding="utf8") as f:
        for i in json.load(f)["List"]:
            precinctPortion_manifest[i["Id"]] = {
                "Portion": i["Description"],
                "PrecinctId": i["PrecinctId"],
            }

    precinct_manifest = {}
    if os.path.isfile(path / "PrecinctManifest.json"):
        with open(path / "PrecinctManifest.json", encoding="utf8") as f:
            for i in json.load(f)["List"]:
                precinct_manifest[i["Id"]] = i["Description"]

    district_manifest = {}
    with open(path / "DistrictManifest.json", encoding="utf8") as f:
        for i in json.load(f)["List"]:
            district_manifest[i["Id"]] = {
                "District": i["Description"],
                "DistrictTypeId": i["DistrictTypeId"],
            }

    districtType_manifest = {}
    with open(path / "DistrictTypeManifest.json", encoding="utf8") as f:
        for i in json.load(f)["List"]:
            districtType_manifest[i["Id"]] = i["Description"]

    districtPrecinctPortion_manifest = {}
    with open(path / "DistrictPrecinctPortionManifest.json", encoding="utf8") as f:
        for i in json.load(f)["List"]:
            districtPrecinctPortion_manifest[i["PrecinctPortionId"]] = i["DistrictId"]

    ballotType_manifest = {}
    with open(path / "BallotTypeManifest.json", encoding="utf8") as f:
        for i in json.load(f)["List"]:
            ballotType_manifest[i["Id"]] = i["Description"]

    countingGroup_manifest = {}
    with open(path / "CountingGroupManifest.json", encoding="utf8") as f:
        for i in json.load(f)["List"]:
            countingGroup_manifest[i["Id"]] = i["Description"]

    ballotTypeContest_manifest = {}
    with open(path / "BallotTypeContestManifest.json", encoding="utf8") as f:
        for i in json.load(f)["List"]:

            if i["ContestId"] not in ballotTypeContest_manifest.keys():
                ballotTypeContest_manifest[i["ContestId"]] = []

            ballotTypeContest_manifest[i["ContestId"]].append(i["BallotTypeId"])

    tabulator_manifest = {}
    with open(path / "TabulatorManifest.json", encoding="utf8") as f:
        for i in json.load(f)["List"]:
            tabulator_manifest[i["Id"]] = i["VotingLocationName"]

    # read in ballots
    ballot_ranks = []
    ballot_IDs = []
    ballot_precinctPortions = []
    ballot_precincts = []
    ballot_types = []
    ballot_countingGroups = []
    ballot_votingLocation = []
    ballot_district = []
    ballot_districtType = []

    some_ballots_are_strings=False
    stringballotnumber=0

    for cvr_export in path.glob("CvrExport*.json"):
        with open(cvr_export, encoding="utf8") as f:
            for contests in json.load(f)["Sessions"]:

                # ballotID
                ballotID_search = re.search("Images\\\\(.*)\*\.\*", contests["ImageMask"])
                if ballotID_search:
                    ballotID = ballotID_search.group(1)
                else:
                    raise RuntimeError("regex is not working correctly. debug")

                countingGroup = countingGroup_manifest[contests["CountingGroupId"]]

                # voting location for ballots
                ballotVotingLocation = tabulator_manifest[contests["TabulatorId"]]

                # for each session use original, or if isCurrent is False,
                # use modified
                if contests["Original"]["IsCurrent"]:
                    current_contests = contests["Original"]
                else:
                    current_contests = contests["Modified"]

                # precinctId for this ballot
                try:
                    precinctPortion = precinctPortion_manifest[current_contests["PrecinctPortionId"]]["Portion"]
                except:
                    print('current_contests["PrecinctPortionId"')
                    print(current_contests["PrecinctPortionId"])

                precinctId = precinctPortion_manifest[current_contests["PrecinctPortionId"]]["PrecinctId"]

                precinct = None
                if precinct_manifest:
                    precinct = precinct_manifest[precinctId]

                # ballotType for this ballot
                ballotType = ballotType_manifest[current_contests["BallotTypeId"]]

                # district for ballot
                ballotDistrictId = districtPrecinctPortion_manifest[current_contests["PrecinctPortionId"]]
                ballotDistrict = district_manifest[ballotDistrictId]["District"]
                ballotDistrictType = districtType_manifest[district_manifest[ballotDistrictId]["DistrictTypeId"]]

                ballot_contest_marks = None


                for cards in current_contests["Cards"]:
                    total_cards += 1
                    if detailedOvervote == True:
                        has_outstack_7 = False  # Flag to indicate if OutstackConditionId 7 is found
                        for ballot_contest in cards["Contests"]:
                            # Check if any mark in the contest has OutstackConditionId of 7
                            if any(7 in mark.get("OutstackConditionIds", []) for mark in ballot_contest.get("Marks", [])):
                                #if any(7 in mark.get("OutstackConditionIds", []) and mark.get("Rank") == 1 for mark in ballot_contest.get("Marks", [])):
                                has_outstack_7 = True
                                break  # Exit the inner loop once we find a 7

                        # After checking all contests in a card, increment the counter if necessary
                        if has_outstack_7:
                            cards_with_outstack_7 += 1

                    # This part remains outside the detailedOvervote check as it's essential for the main logic
                    for ballot_contest in cards["Contests"]:
                        if ballot_contest["Id"] == current_contest_id:
                            if ballot_contest_marks is not None:
                                raise RuntimeError("Contest Id appears twice across a single set of cards. Not expected.")
                            ballot_contest_marks = ballot_contest["Marks"]

                # After the loop, only print if detailedOvervote is True
                #if detailedOvervote == True:
                #    break

                # skip ballot if didn't contain contest
                if ballot_contest_marks is None:
                    continue

                #skip if ballot was a string/redacted, store string
                if isinstance(ballot_contest_marks, str) == True:
                    stringballotnumber+=1
                    if some_ballots_are_strings == False:
                        print("Some ballots are strings, they have been skipped")
                        some_ballots_are_strings = True
                    continue


                #dealwith outstack conditionasl
                found7=False
                FalseVote=False
                C1=False
                C2=False
                C3=False
                C3_1=False
                C4=False
                found0, found1, found2, found5, found4, found6, found9, found10, found11, found12, found13, found14 = (
                False, False, False, False, False, False, False, False, False, False, False, False)
                foundlowmark=False


                for i in ballot_contest_marks:
                    if detailedOvervote == True:
                        saved_outstack_ids.update(set(map(str, i["OutstackConditionIds"])))

                        countgroup_id = int(contests["CountingGroupId"])
                        allcountinggroup[countgroup_id] = allcountinggroup.get(countgroup_id, 0) + 1

                        if 7 in i["OutstackConditionIds"] and i["Rank"]==1:
                            found7 = True
                            saved_7card_ids.update({int(cards["Id"])})
                            saved_7ballottype.update({int(current_contests["BallotTypeId"])})

                            precinct_id = int(current_contests["PrecinctPortionId"])
                            saved_7precinctportion[precinct_id] = saved_7precinctportion.get(precinct_id, 0) + 1

                            #countgroup_id = int(contests["CountingGroupId"])
                            saved_7countinggroup[countgroup_id] = saved_7countinggroup.get(countgroup_id, 0) + 1

                            Record_id = int(contests["RecordId"])
                            saved_7Record[Record_id] = saved_7Record.get(Record_id, 0) + 1

                            BatchID = int(contests["BatchId"])
                            saved_7Batch[BatchID] = saved_7Batch.get(BatchID, 0) + 1

                            Tabulator = int(contests["TabulatorId"])
                            saved_7Tabulator[Tabulator] = saved_7Tabulator.get(Tabulator, 0) + 1

                            if detailedOvervote == True and printedballotyet < 10:
                                printedballotyet += 1
                                print("")
                                print(ballot_contest_marks)
                                print()



                    if i["MarkDensity"] < 50 and i["Rank"]==1 and i["IsAmbiguous"]==False:

                        foundlowmark=True
                        if detailedOvervote == True and printedballotyet < 0:
                            printedballotyet += 1
                            print("")
                            print(ballot_contest_marks)
                            print()

                    if 0 in i["OutstackConditionIds"] and i["Rank"]==1:
                        found0 = True



                    if i["IsVote"]==False and i["Rank"]==1 and i["IsAmbiguous"]==False:
                        FalseVote = True

                    if i["IsVote"]==False and i["Rank"]==1 and i["IsAmbiguous"]==False and 7 not in i["OutstackConditionIds"]:
                        C1=True

                    if i["Rank"]==1 and i["IsAmbiguous"]==True:
                        C2=True
                    if  7 in i["OutstackConditionIds"] and i["IsVote"]==False:
                        C3=True
                    if  7 in i["OutstackConditionIds"] and i["IsVote"]==False and i["Rank"]==1:
                        C3_1=True

                    if  7 in i["OutstackConditionIds"] and i["IsVote"]==True:
                        C4=True

                    if 1 in i["OutstackConditionIds"] and i["Rank"] == 1:
                        found1 = True

                    if 2 in i["OutstackConditionIds"] and i["Rank"] == 1:
                        found2 = True

                    if 5 in i["OutstackConditionIds"] and i["Rank"] == 1:
                        found5 = True

                    if 4 in i["OutstackConditionIds"] and i["Rank"] == 1:
                        found4 = True

                    if 6 in i["OutstackConditionIds"] and i["Rank"] == 1:
                        found6 = True

                    if 9 in i["OutstackConditionIds"] and i["Rank"] == 1:
                        found9 = True

                    if 10 in i["OutstackConditionIds"] and i["Rank"] == 1:
                        found10 = True

                    if 11 in i["OutstackConditionIds"] and i["Rank"] == 1:
                        found11 = True

                    if 12 in i["OutstackConditionIds"] and i["Rank"] == 1:
                        found12 = True

                    if 13 in i["OutstackConditionIds"] and i["Rank"] == 1:
                        found13 = True

                    if 14 in i["OutstackConditionIds"] and i["Rank"] == 1:
                        found14 = True


                if detailedOvervote == True:
                    if C1==True:
                        C1Count+=1
                    if C2==True:
                        C2Count+=1
                    if C3==True:
                        C3Count+=1
                    if C3_1==True:
                        C3_1Count+=1
                    if C4==True:
                        C4Count+=1

                    if foundlowmark==True:
                        lowmarkunambigiouscount +=1

                    if found0==True:
                        O0Count+=1

                    if found1 == True:
                        O1Count += 1

                    if found2 == True:
                        O2Count += 1

                    if found5 == True:
                        O5Count += 1

                    if found4 == True:
                        O4Count += 1

                    if found6 == True:
                        O6Count += 1

                    if found9 == True:
                        O9Count += 1

                    if found10 == True:
                        O10Count += 1

                    if found11 == True:
                        O11Count += 1

                    if found12 == True:
                        O12Count += 1

                    if found13 == True:
                        O13Count += 1

                    if found14 == True:
                        O14Count += 1

                    if FalseVote==True:
                        falsevotenumber+=1
                        if detailedOvervote == True and printedballotyet < 0:
                            printedballotyet += 1
                            print()
                            print(ballot_contest_marks)
                            print()
                    if found7==True:
                        outstackconditionalnumber +=1

                    if FalseVote==False and found7==True:
                        NotFalseis7+=1

                    #raiseError("non false 7")

                # check for marks on each rank expected for this contest
                currentRank = 1
                current_ballot_ranks = []


                while currentRank <= current_contest_rank_limit:

                    # find any marks that have the currentRank and aren't Ambiguous and aren't strings
                    #currentRank_marks = [i for i in ballot_contest_marks if i["Rank"] == currentRank and i["IsAmbiguous"] is False]
                    #currentRank_marks = [i for i in ballot_contest_marks if i["Rank"] == currentRank and i["IsAmbiguous"] is False and i["Rank"] != "***Redacted***"]
                    #currentRank_marks = [i for i in ballot_contest_marks if isinstance(i, dict) and i.get("Rank") == currentRank and i.get("IsAmbiguous") is False]
                    #print(ballot_contest_marks)




                    #Seven in outstack conditional IDs added for Alaska thingy
                    #currentRank_marks = [i for i in ballot_contest_marks if i["Rank"] == currentRank and i["IsAmbiguous"] is False and (i["OutstackConditionIds"] is None or 7 not in i["OutstackConditionIds"])]
                    currentRank_marks = [i for i in ballot_contest_marks if i["Rank"] == currentRank and i["IsVote"] is True  and (i["OutstackConditionIds"] is None or 7 not in i["OutstackConditionIds"])]

                    currentCandidate = "**error**"

                    if len(currentRank_marks) == 0:
                        currentCandidate = BallotMarks.SKIPPED
                    elif len(currentRank_marks) > 1:
                        if detailedOvervote == True and currentRank == 1:
                            #newlist=[]
                            #for i in currentRank_marks: newlist.append(candidate_manifest[i["CandidateId"]])
                            newlist= [candidate_manifest[i["CandidateId"]] for i in currentRank_marks]
                            #print(newlist)
                            newlist.sort()
                            overvotelist.append(newlist)
                            currentCandidate = BallotMarks.OVERVOTE #", ".join(newlist)
                        else:
                            currentCandidate = BallotMarks.OVERVOTE

                    else:
                        currentCandidate = candidate_manifest[currentRank_marks[0]["CandidateId"]]

                    if currentCandidate == "**error**":
                        raise RuntimeError("error in filtering marks. debug")

                    current_ballot_ranks.append(currentCandidate)
                    currentRank += 1


                ballot_ranks.append(current_ballot_ranks)
                ballot_precinctPortions.append(precinctPortion)
                ballot_precincts.append(precinct)
                ballot_IDs.append(ballotID)
                ballot_types.append(ballotType)
                ballot_countingGroups.append(countingGroup)
                ballot_votingLocation.append(ballotVotingLocation)
                ballot_district.append(ballotDistrict)
                ballot_districtType.append(ballotDistrictType)

    ballot_dict = {
        "ranks": ballot_ranks,
        "weight": [decimal.Decimal("1")] * len(ballot_ranks),
        "ballotID": ballot_IDs,
        "precinct": ballot_precincts,
        "precinctPortion": ballot_precinctPortions,
        "ballot_type": ballot_types,
        "countingGroup": ballot_countingGroups,
        "votingLocation": ballot_votingLocation,
        "district": ballot_district,
        "districtType": ballot_districtType,
    }

    # make sure precinctManifest was part of CVR, otherwise exclude precinct column
    if len(ballot_precincts) != sum(i is None for i in ballot_precincts):
        ballot_dict["precinct"] = ballot_precincts

    # check ballotIDs are unique
    if len(set(ballot_dict["ballotID"])) != len(ballot_dict["ballotID"]):
        raise RuntimeError("some non-unique ballot IDs")
    print(f"Total number of cards: {total_cards}")
    print("number of string ballots counted: ",stringballotnumber)
    if detailedOvervote == True:
        print(f"Number of cards with OutstackConditionId 7: {cards_with_outstack_7}")

        overvotesdf=pd.DataFrame({'Rank1Overvotes':overvotelist})
        overvotesdf.to_csv("Overvotes.csv")
        #print("number of string ballots counted: ",stringballotnumber)
        print('number of ballots with at least one "Invalid contest" ranking:',outstackconditionalnumber)
        print('number of ballots with "IsVote":false rankings',falsevotenumber)
        print("saved_outstack_ids:",saved_outstack_ids)
        print("notFalseis7:",NotFalseis7)
        print("Ambiguous votes ",AmbigiousCount)
        print("NOn-ambigous,non7,rank1,IsFalse",C1Count)
        print("ambigous,rank1",C2Count)
        print("IsFalse,7:",C3Count)
        print("IsFalse,7,rank1:",C3_1Count)
        print("IsTrue,7:",C4Count)
        print("Outstack Rank1 Ambiguous,",O0Count)
        print("Outstack Rank1 Writein,",O1Count)
        print("Outstack Rank1 BlankBallot,",O2Count)
        print("Outstack Rank1 Overvote,",O5Count)
        print("Outstack Rank1 Undervote,",O4Count)
        print("Outstack Rank1 BlankContest,",O6Count)
        print("Outstack Rank1 OvervotedRanking,",O9Count)
        print("Outstack Rank1 InconsistentRcvOrdering,",O10Count)
        print("Outstack Rank1 SkippedRanking,",O11Count)
        print("Outstack Rank1 DuplicatedRcvCandidate,",O12Count)
        print("Outstack Rank1 UnvotedRcvContest,",O13Count)
        print("Outstack Rank1 UnusedRanking,",O14Count)
        print("marked unambiogus less than 90 mark,",lowmarkunambigiouscount)
        print(len(saved_7card_ids),",number of ballots iwth 7 card")
        print("7 card ids,",saved_7card_ids)
        print("min 7 card id,",min(saved_7card_ids))
        print("max 7 card id,",max(saved_7card_ids))
        print(len(saved_7ballottype),",number of ballot types")
        print("ballot types,",saved_7ballottype)
        print("precinct portion 7 card len,",len(saved_7precinctportion))
        print("7 precinctportion,",saved_7precinctportion)
        print("min precinctportion,",min(saved_7precinctportion))
        print("max precinctportion,",max(saved_7precinctportion))
        print("counting groups,",saved_7countinggroup)
        print("all count groups,",allcountinggroup)
        print("Record ID Len,",len(saved_7Record))
        print("Record ID min,",min(saved_7Record))
        print("Record ID max,",max(saved_7Record))
        print("Batches,",saved_7Batch)
        print("tabulators,",saved_7Tabulator)




    return ballot_dict


def candidate_column_csv_old(cvr_path: Union[str, pathlib.Path]) -> Dict[str, List]:
    """
    Reads ballot ranking information stored in csv file called "cvr.csv".
    Candidate column names. One ballot per row, with ranks given to candidates in cell rows.

    Candidate columns are identified by reading a "candidate_codes.csv" file. Columns present in the CVR file that are not listed in the candidate codes are parsed as auxillary ballot information (precinct ID, etc).

    :param cvr_path: The path to the directory containing the CVR and candidate codes files.
    :type cvr_path: Union[str, pathlib.Path]
    :raises RuntimeError: Error raised if not all parsed rank lists are the same length.
    :return: A dictionary of lists containing all columns in the CVR file. Rank columns are combined into per-ballot lists and stored with the key 'ranks'. A 'weight' key and list of 1's is added to the dictionary if no 'weight' column exists. All weights are of type :class:`decimal.Decimal`.
    :rtype: Dict[str, List]
    """

    cvr_path = pathlib.Path(cvr_path)

    cvr = pd.read_csv(cvr_path / "cvr.csv", encoding="utf8")
    candidate_codes = pd.read_csv(cvr_path / "candidate_codes.csv", encoding="utf8")

    candidate_dict = {str(code): cand for code, cand in zip(candidate_codes["code"], candidate_codes["candidate"])}

    max_rank_num = int(cvr[candidate_dict.keys()].max().max())
	# I need to add a test to add in overvotes. like there is for skipped or somethingcurrentCandidate = BallotMarks.OVERVOTE
	#over votes is missing

    ballots = []
    for _, row in cvr.iterrows():
        row_ranks = {
            int(row[code]): candidate_dict[code]
            for code, value in candidate_dict.items()
            if value and not pd.isna(row[code])
        }
        print(row_ranks)


        ballot = []

        for rank_num in range(1, max_rank_num + 1):
            if rank_num in row_ranks:
                #PSEUDOCODE if rank_num in ballot:
                #    replac
                ballot.append(row_ranks[rank_num])
            else:
                ballot.append(BallotMarks.SKIPPED)
        ballots.append(ballot)

    ballot_dict = {"ranks": ballots}
    for col in cvr.columns:
        if col not in candidate_dict:
            ballot_dict[col] = cvr[col]

    return ballot_dict

