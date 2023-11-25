import locale

def format_as_dollar_amount(number):
    if isinstance(number, str) and number.isdigit():
        number = int(number)
        
    # Set the locale to the user's default setting
    locale.setlocale(locale.LC_ALL, '')

    # Format the number as a dollar amount
    formatted_amount = locale.currency(number, grouping=True)

    return formatted_amount

template = '''
  <style>
    body {{
      font-family: Arial, sans-serif;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }}

    th, td {{
      border: 1px solid #ddd;
      padding: 10px;
      text-align: left;
    }}

    th {{
      background-color: #f2f2f2;
    }}

    .increase {{
      color: green;
      font-weight: bold;
    }}

    .decrease {{
      color: red;
      font-weight: bold;
    }}
  </style>
</head>
<body>

  <h2>Car Price Changes</h2>

  <table>
    <thead>
      <tr>
        <th>Car Model</th>
        <th>Previous Price</th>
        <th>New Price</th>
        <th>Change</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      <!-- Add more rows for other car models -->
    </tbody>
  </table>

</body>
'''

def format_html(comparisonDict):
    notification = ''
    for car in comparisonDict:
            if comparisonDict[car]['new_price'] == -1: #car has sold
                notification += f'''
                <tr>
                    <td>{comparisonDict[car]['title'] + ' - ' + comparisonDict[car]['subtitle']}</td>
                    <td>{format_as_dollar_amount(comparisonDict[car]['old_price'])}</td>
                    <td >--</td>
                    <td class="decrease">No Longer Listed</td>
                </tr>\n'''
            elif not 'old_price' in comparisonDict[car]: #car is brand new
                notification += f'''
                <tr>
                    <td>{comparisonDict[car]['title'] + ' - ' + comparisonDict[car]['subtitle']}</td>
                    <td>--</td>
                    <td >{format_as_dollar_amount(comparisonDict[car]['new_price'])}</td>
                    <td class="decrease">Initial Listing</td>
                </tr>\n'''
            else:
                if not comparisonDict[car]['old_price'] == comparisonDict[car]['new_price']:
                    if comparisonDict[car]['old_price'] > comparisonDict[car]['new_price']: #price decrease
                        notification += f'''
                        <tr>
                            <td>{comparisonDict[car]['title'] + ' - ' + comparisonDict[car]['subtitle']}</td>
                            <td>{format_as_dollar_amount(comparisonDict[car]['old_price'])}</td>
                            <td class="decrease">{format_as_dollar_amount(comparisonDict[car]['new_price'])}</td>
                            <td class="decrease">{format_as_dollar_amount(int(comparisonDict[car]['new_price']) - int(comparisonDict[car]['old_price']))}</td>
                        </tr>\n'''
                    else: #price increase
                        notification += f'''
                        <tr>
                            <td>{comparisonDict[car]['title'] + ' - ' + comparisonDict[car]['subtitle']}</td>
                            <td>{format_as_dollar_amount(comparisonDict[car]['old_price'])}</td>
                            <td class="increase">{format_as_dollar_amount(comparisonDict[car]['new_price'])}</td>
                            <td class="increase">+{format_as_dollar_amount(int(comparisonDict[car]['new_price']) - int(comparisonDict[car]['old_price']))}</td>
                        </tr>\n'''

                         
                    #notification += 'Price change for ' + comparisonDict[car]['title'] + ' - ' + comparisonDict[car]['subtitle'] + ': ' + format_as_dollar_amount(comparisonDict[car]['old_price']) +'->'+format_as_dollar_amount(comparisonDict[car]['new_price'])

    if notification == '':
        return 'Text', 'No Inventory changes found'
    else:
        return 'Html', template.format(rows=notification)