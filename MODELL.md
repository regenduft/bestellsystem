This File describes the concept of the data structure in the backend for this ordering tool.

## We need in general the following entries:
Properties which are embraced are properties which are not necessarily needed.

#### General responsibilities:
- Admins
- Oderingadmins ...

#### SoLaWi products entries:
- flag orderable
- (max number orderable at once)
- flag exchangeable (not needed if standard IV value is 0 and if you can't exchange 0 value Products)
- interchanging value (IV) measured in piece Beard (or whatever) with default 0 for not changeable
- flag modular 
  - period of module time
  - optional price in €
- list of (type, package sizes) tuples

The question arises if we want a sellable flag here or if we want to manage this with the weekly baskets. If we do this with weekly baskets we reduce complexity. An other question is should a "user" be able to change his basket?  (Status quo is with weekly baskets)

#### Depot entries:
- Depotbesteller, ... and probably more orga people
- Sharholders of Depot List

ii. We need to decide whether the depots store the entries of the people being part of it or the shareholders store have an entry with Depot. Mind that we haven some people without Depot or rather picking up form Nussloch directly. I prefer to link shareholders in the depot and have a singlebox holder depot to be more structured and be able to have new depots.

#### SoLaWi shareholders entry
- type of weekly basket
- Number of shares (positive integer or 0,5 for small share)
- Saldo in IV (strictly positive with max capacity of 8 weekly baskets) momentary order included 

ii. When initializing a new one ask for Depot, and type of weekly basket (e.g. sell meat).
	

#### Changeable weekly capacity-baskets/ standard order as collection of products
- a list of tuples with amount, (packagesize) and product
- (summed IV of product in basket)
	
	
## for the ordering:
#### momentary/ next order per shareholder
- regularly module order, exchange, deorderd products 
  - regularly order of modules (extra vegetables are modules)
    - point of next possible change 
  - regularly deorder
  - regularly exchange
    - tuple (product to change form, to change into)
    - ( expireing date )
    - saldo saved till now -> aprox. week of next order
    - ( period of ordering if not to complicated)

- one time products:
  - sepzial products: 
    bread, with type preference
  - notes per product or order

ii. multiple week deordering all for vacation, should the bread sum into saldo?
    If bread isn't orderable reduce amount of bread in weekly basket -1

## views needed for the packing and ordering process:
 All overviews need to have a present and past version.
#### overview of past orderings per shareholder: 

#### overview of each depot:
- oder per member
- total oder 

#### view total orders of all depots:

#### view total bread order with preferences per depot:

#### view of modular products:
	e.g. hearbs, quark, extra vegetables (cheese)...

## comments regarding the interface:

The ii. lines are notes regarding the interface.
We need to decide the date, when the weekly oder is closing.
An E-Mail should be sent to persons in charge (see administration layer, Depotadmins, Oderingadmins, ...) in PDF format (or excel whatever is best)

Bread:
#### We need the following administration layers.
- Fulladmins
- Depotadmins (push to other depot function with notification to other depotadmin?, acess to depot overview, able to change momentary (and last week or all?) orderings)
- Oderingadmins (aces to all overviews, Products aces, weekly basket change, full past ordering aces)
- Userlevel (change momentary and regular ordering, view last orders)

