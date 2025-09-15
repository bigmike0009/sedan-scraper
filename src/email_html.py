import locale

def format_as_dollar_amount(number):
    if isinstance(number, str) and number.isdigit():
        number = int(number)
        
    locale.setlocale(locale.LC_ALL, '')  # Set the locale to the user's default setting
    formatted_amount = locale.currency(number, grouping=True)
    return formatted_amount

template = '''
<body style="font-family: Arial, sans-serif;">

  <h2 style="text-align: left; color: #333;">Car Price Changes</h2>

  <table style="width: 100%; border-collapse: collapse; margin-top: 20px; border: 2px solid #ddd;">
    <thead>
      <tr>
        <th style="background-color: #f2f2f2; border: 1px solid #ddd; padding: 12px 20px; text-align: left;">VIN</th>
        <th style="background-color: #f2f2f2; border: 1px solid #ddd; padding: 12px 20px; text-align: left;">Car Model</th>
        <th style="background-color: #f2f2f2; border: 1px solid #ddd; padding: 12px 20px; text-align: left;">Previous Price</th>
        <th style="background-color: #f2f2f2; border: 1px solid #ddd; padding: 12px 20px; text-align: left;">New Price</th>
        <th style="background-color: #f2f2f2; border: 1px solid #ddd; padding: 12px 20px; text-align: left;">Change</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>

</body>
'''

# Define a variable for common TD styles
td_style = "border: 1px solid #ddd; padding: 12px 20px;"

def format_html(comparisonDict):
    notification = ''
    for vin, car_data in comparisonDict.items():
        title = car_data.get('title', '')
        subtitle = car_data.get('subtitle', '')
        old_price = car_data.get('old_price')
        new_price = car_data.get('new_price')

        if new_price == -1:  # Car has sold
            notification += f'''
            <tr>
                <td style="{td_style}">{vin}</td>
                <td style="{td_style}">{title} - {subtitle}</td>
                <td style="{td_style}">{format_as_dollar_amount(old_price)}</td>
                <td style="{td_style}">--</td>
                <td style="{td_style} color: red; font-weight: bold;">No Longer Listed</td>
            </tr>\n'''
        elif old_price is None:  # Car is brand new
            notification += f'''
            <tr>
                <td style="{td_style}">{vin}</td>
                <td style="{td_style}">{title} - {subtitle}</td>
                <td style="{td_style}">--</td>
                <td style="{td_style}">{format_as_dollar_amount(new_price)}</td>
                <td style="{td_style} color: blue; font-weight: bold;">Initial Listing</td>
            </tr>\n'''
        else:
            if old_price != new_price:
                change_amount = int(new_price) - int(old_price)
                change_color = "green" if change_amount > 0 else "red"
                change_sign = "+" if change_amount > 0 else ""

                notification += f'''
                <tr>
                    <td style="{td_style}">{vin}</td>
                    <td style="{td_style}">{title} - {subtitle}</td>
                    <td style="{td_style}">{format_as_dollar_amount(old_price)}</td>
                    <td style="{td_style} color: {change_color}; font-weight: bold;">{format_as_dollar_amount(new_price)}</td>
                    <td style="{td_style} color: {change_color}; font-weight: bold;">{change_sign}{format_as_dollar_amount(change_amount)}</td>
                </tr>\n'''

    if not notification:
        return 'Text', 'No Inventory changes found'
    return 'Html', template.format(rows=notification)
