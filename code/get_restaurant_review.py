import json
import pandas
from clean_reviews import *


def select_attrs_and_remove_other(obj, attrs_set):
    for attr in list(obj.keys()):
        if attr not in attrs_set:
            obj.pop(attr, None)

    remaining_attrs_set = set(obj.keys())
    diff = sorted(list(attrs_set - remaining_attrs_set))
    if diff:
        print("Error: the attributes %s do not belong to obj!" % (str(diff)))


def replace_spaces_in_one_key_with_underscores(obj, key):
    if " " in key or "-" in key:
        new_key = key.replace(" ", "_").replace("-", "_")
        obj[new_key] = obj[key]
        obj.pop(key, None)


def add_attr_if_not_existed(obj, attr=None, default_value=None):
    if attr not in obj:
        obj[attr] = default_value


def replace_spaces_in_all_keys_with_underscores(obj):
    for key in list(obj.keys()):
        replace_spaces_in_one_key_with_underscores(obj, key)


def calculate_size_of_a_list_attr(user_obj, list_attr):
    n_attr = ''.join(["n", list_attr])
    if list_attr in user_obj:
        user_obj[n_attr] = len(user_obj[list_attr])
    else:
        print(''.join(['This guy - ', user_obj["user_id"], ' - has no',
                        list_attr, '!']))
        user_obj[n_attr] = 0


def reduce_user_data_attr(user_obj, attr):
    sum = 0
    for category in user_obj[attr]:
        sum += user_obj[attr][category]
    user_obj[attr] = sum


def flatten_one_data_attr(obj, attr):
    for category in obj[attr]:
        new_attr = ''.join([attr, '.', category])
        obj[new_attr] = obj[attr][category]
    obj.pop(attr, None)


def flatten_all_data_attr_recursively(obj):
    is_still_need_flattening = True
    while is_still_need_flattening:
        replace_spaces_in_all_keys_with_underscores(obj)
        is_still_need_flattening = False
        for attr in list(obj.keys()):
            if isinstance(obj[attr], dict):
                is_still_need_flattening = True
                flatten_one_data_attr(obj, attr)


def convert_time_to_numeric(hour_str):
    hour = float(hour_str.split(":")[0])
    minutes = float(hour_str.split(":")[1])
    return (hour + minutes/60.0)


def calculate_opening_hours_per_day(opening_closing_times):
    opening_time = convert_time_to_numeric(opening_closing_times["open"])
    closing_time = convert_time_to_numeric(opening_closing_times["close"])
    if closing_time < opening_time:
        closing_time += 24.0
    return (closing_time - opening_time)


def calculate_hours_per_week(business_obj):
    hours_each_day = business_obj["hours"]
    hours_per_week = 0
    for opening_closing_times in hours_each_day.values():
        hours_per_week += calculate_opening_hours_per_day(opening_closing_times)

    business_obj["hours_per_week"] = hours_per_week


def improve_category_naming(business_obj):
    if "categories" not in business_obj:
        print("[WARNING] improve_category_naming: business id \"%s\" does"
                " not belong to any categories!" %
                (business_obj["business_id"]))
        return
    for i in range(0, len(business_obj["categories"])):
        business_obj["categories"][i] = business_obj["categories"][i].replace(' ', '_')


def add_business_to_categories(business_obj, business_categories):
    if "categories" not in business_obj:
        print("[WARNING] add_business_to_categories: business id \"%s\" does"
                " not belong to any categories!" %
                (business_obj["business_id"]))
        return

    for category in business_obj["categories"].split(';'):
        tmp_dict = dict()
        add_attr_if_not_existed(business_categories, attr=category,
                                default_value=tmp_dict)
        add_attr_if_not_existed(business_categories[category], attr="category",
                                default_value=category)
        add_attr_if_not_existed(business_categories[category],
                                attr="nbusinesses", default_value=0)
        add_attr_if_not_existed(business_categories[category],
                                attr="nreviews", default_value=0)
        business_categories[category]["nbusinesses"] += 1


def add_review_to_categories(review_obj, business_dict, business_categories):
    business_obj = business_dict[review_obj["business_id"]]
    for category in business_obj["categories"].split(';'):
        try:
            business_categories[category]["nreviews"] += 1
        except:
            print("ERROR: id=%s, cats=%s" % (str(business_obj["business_id"]), str(business_obj["categories"])))


def join_business_categories(obj):
    if "categories" not in obj:
        obj["categories"] = []
    obj["categories"] = ';'.join(obj["categories"])


def parse_address_for_zipcode(address):
    try:
        zipcode = int(address.split(" ")[-1])
    except:
        zipcode = -1
    return zipcode


def extract_zipcode_of_business(business_obj):
    business_obj["zipcode"] = parse_address_for_zipcode(business_obj["full_address"])


def clean_data_user(input_file):
    selected_attrs_set = set(["average_stars", "compliments", "fans", "name",
                            "nelite", "nfriends", "review_count", "user_id",
                            "votes", "yelping_since"])

    with open(input_file, "r") as f:
        lines = f.readlines()

    user_dict = dict()
    for i in range(0, len(lines)):
        user_obj = json.loads(lines[i])
        calculate_size_of_a_list_attr(user_obj, 'friends')
        calculate_size_of_a_list_attr(user_obj, 'elite')
        reduce_user_data_attr(user_obj, 'compliments')
        reduce_user_data_attr(user_obj, 'votes')
        # reset review_count so that we can recount later
        user_obj["review_count"] = 0.0
        select_attrs_and_remove_other(user_obj, selected_attrs_set)
        user_dict[user_obj["user_id"]] = user_obj

    return user_dict


def summarize_parking_attribute(business_obj):
    for attr in business_obj:
        if "attributes.Parking." in attr:
            business_obj["attributes.ParkingAvail"] |= business_obj[attr]


def clean_data_business(input_file):
    selected_attrs_set = set(["business_id", "name", "state", "city", "zipcode",
                              "hours_per_week", "stars", "review_count", "attributes.Good_for_Kids",
                              "attributes.Takes_Reservations", "attributes.ParkingAvail", "attributes.Delivery",
                              "attributes.Accepts_Credit_Cards", "attributes.Waiter_Service", "attributes.Smoking",
                              "attributes.Drive_Thru",
                              "categories"])

    business_dict = dict()
    business_categories = dict()
    with open(input_file, "r") as f:
        for line in f:
            business_obj = json.loads(line)
            calculate_hours_per_week(business_obj)
            flatten_all_data_attr_recursively(business_obj)
            add_attr_if_not_existed(business_obj, attr="attributes.Good_for_Kids",
                                    default_value=False)
            add_attr_if_not_existed(business_obj, attr="attributes.Takes_Reservations",
                                    default_value=False)
            add_attr_if_not_existed(business_obj, attr="attributes.ParkingAvail",
                                    default_value=False)
            add_attr_if_not_existed(business_obj, attr="attributes.Delivery",
                                    default_value=False)
            add_attr_if_not_existed(business_obj, attr="attributes.Accepts_Credit_Cards",
                                    default_value=False)
            add_attr_if_not_existed(business_obj, attr="attributes.Waiter_Service",
                                    default_value=False)
            add_attr_if_not_existed(business_obj, attr="attributes.Smoking", default_value=False)
            add_attr_if_not_existed(business_obj, attr="attributes.Drive_Thru",
                                    default_value=False)
            add_attr_if_not_existed(business_obj, attr="tip_count",
                                    default_value=0)
            summarize_parking_attribute(business_obj)
            extract_zipcode_of_business(business_obj)
            improve_category_naming(business_obj)
            join_business_categories(business_obj)
            add_business_to_categories(business_obj, business_categories)
            select_attrs_and_remove_other(business_obj, selected_attrs_set)
            business_dict[business_obj["business_id"]] = business_obj

    return business_dict, business_categories


def clean_one_review(review_obj, business_obj, col_names_set):
    """ Clean one review, returning the dictionary containing all the
    relevant features of a review, ready for the prediction.
    """
    results = {col_name: 0 for col_name in col_names_set}
    results["business_id"] = business_obj["business_id"]
    results["date"] = review_obj["date"]

    # determine the rating level
    if review_obj["stars"] <= 2:
        results["IsRatingBad"] = 1
    elif review_obj["stars"] < 4:
        results["IsRatingModerate"] = 1
    else:
        results["IsRatingGood"] = 1

    review_text = review_obj["text"]
    review_ngrams = extract_unigrams(review_text) \
                    + extract_bigrams(review_text) \
                    + extract_trigrams(review_text)
    for ngram in review_ngrams:
        if ngram in results:
            results[ngram] = 1

    return results


def clean_data_review(input_file, business_dict,
                        business_categories, restaurants_df):
    """ Clean the review data for Restaurants only.
    Return a pandas DataFrame
    """
    df = pandas.read_csv(TRAIN_DATA_PATH, nrows=0)
    # Add a new column for recording the corresponding business_id
    df['business_id'] = []
    df['date'] = []
    col_names_set = set(df.columns)

    # pick the 3 most popular restaurants
    pop_restaurants = set(restaurants_df["business_id"][:3])

    review_restaurants_count = 0
    reviewed = 0
    with open(input_file, "r") as f:
        for line in f:
            reviewed += 1
            review_obj = json.loads(line)
            add_review_to_categories(review_obj, business_dict,
                                        business_categories)
            business_id = review_obj["business_id"]
            business_obj = business_dict[business_id]
            if not reviewed % 100:
                print "Reviewed: %d" % reviewed
            if business_id in pop_restaurants:
                # to eliminate cases with invalid dates
                one_cleaned_review = clean_one_review(review_obj, business_obj,
                                                        col_names_set)
                df = df.append(one_cleaned_review, ignore_index=True)
                review_restaurants_count += 1

    print('Final review_restaurants_count = %d' % review_restaurants_count)
    return df


def get_restaurants(business_dict):
    restaurants_df = pandas.DataFrame(columns=["business_id", "name",
                                                "review_count"])
    for biz in business_dict.values():
        if "Restaurants" in biz["categories"]:
            restaurants_df = restaurants_df.append(
                {"business_id": biz["business_id"],
                    "name": biz["name"], "review_count": biz["review_count"]},
                ignore_index=True)
    return restaurants_df.sort_values(by=["review_count"], ascending=[False])


if __name__ == "__main__":
    DATA_BUSINESS = '/Users/liuyang/Downloads/yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_business.json'
    DATA_REVIEW = '/Users/liuyang/Downloads/yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_review.json'
    DATA_BUSINESS_CLEANED = '/Users/liuyang/Downloads/yelp_dataset_challenge_academic_dataset/business_cleaned.csv'
    DATA_BUSINESS_CATEGORIES_CLEANED = '/Users/liuyang/Downloads/yelp_dataset_challenge_academic_dataset/business_category_cleaned.csv'
    DATA_REVIEW_CLEANED_RESTAURANTS = '/Users/liuyang/Downloads/yelp_dataset_challenge_academic_dataset/review_cleaned_restaurants.csv'
    DATA_RESTAURANTS = '/Users/liuyang/Downloads/yelp_dataset_challenge_academic_dataset/restaurants.csv'
    TRAIN_DATA_PATH = '/Users/liuyang/Downloads/yelp_dataset_challenge_academic_dataset/train.csv'


    business_dict, business_categories = clean_data_business(DATA_BUSINESS)
    restaurants_df = get_restaurants(business_dict)
    review_df = clean_data_review(DATA_REVIEW, business_dict, business_categories, restaurants_df)

    review_df.to_csv(DATA_REVIEW_CLEANED_RESTAURANTS, index=False, encoding='utf8')
    restaurants_df.to_csv(DATA_RESTAURANTS, index=False, encoding='utf8')
