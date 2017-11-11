This File describes the concept of the data structure in the backend for this ordering tool.
It will not always be up to date, so look into modells.py for more details.

The ii. lines are notes regarding the interface.
We need to decide the date, when the weekly oder is closing.
An E-Mail should be sent to persons in charge (see administration layer, Depotadmins, Oderingadmins, ...) in PDF format (or excel whatever is best)

## We need in general the following entries:
Properties which are embraced are properties which are not necessarily needed.

#### General responsibilities:
- Admins
- Oderingadmins ...

#### SoLaWi products entries:
- flag orderable: default true
- CharField unit: measuring unit of the Product e.g. kg or l
- (max number orderable at once)
- Floatfield Exchange Value (EV) of 1 unit of the Product: default 0 means not exchangeable
- Integerfield Module Time: Time the order of a modular product may not be changed in weeks; default value none means not modular
- Floatfield Price of Modular Product: default none means not modular product
- list of (type, package sizes) tuples

##### Validators:
- validate that if ModuleTime = none that Price of Modular Product = none 

The question arises if we want a sellable flag here or if we want to manage this with the weekly baskets. If we do this with weekly baskets we reduce complexity. An other question is should a "user" be able to change his basket?  (Status quo is with weekly baskets)

##### ProductProperty:
One object is a specific package size for a specific product type of a product.

- Product
- FloatField packagesize
- flag orderable: default true
- CharField producttype

#### Depot entries:
- CharField name
- CharField location

#### SoLaWi shareholders entry (User):
- type of weekly basket
- Depot
- FloatField: Number of shares (positive integer or 0,5 for small share)
- Assets in EV (strictly positive with max capacity of 8 weekly baskets) momentary order included 

ii. The inclusion of the momentary order is needed to order anything currently, but a concept for counter-ordering and regularly ordering is needed e.g. change in counter-ordering is only effektiv for next ordering and initiating a regularly order needs first ordering date, deleting of a regularly order results in a loss of savings.

##### Validators:
- validate Number of shares
- validate Assets

ii. When initializing a new one ask for Depot, and type of weekly basket (e.g. sell meat).
	
## for the ordering:

#### OrderContent:
The Content in products with properties of an order as a ManyToMany relation via Amount.
##### Amount:
The Amount of a specific product with a property in an OrderContent.

#### DefaultBasket:
- content: an OrderContent instance
- CharField name

##### WeeklyBasket:
- counter-order: an OrderContent instance to save the momentary counter-ordered Products
- one Default Basket

#### OrderBasket:
- content: an OrderContent instance
- DateField week: the week of the order
- user: the "owner" of the Order

#### RegularyOrder:
- User
- product with property
- amount: the amount of the product to be ordered
- savings: amount of EV still saved for this RegularyOrder
- period: the period the order is to be ordered in
- ( expiring date if needed )

##### Validators:
- if product is modular validate that savings are null (this means always orderable)

ii. Modular implies always ordered and delivered when delivered

ii. Multiple week counter-ordering all for vacation, should the bread sum into Saldo?
    If bread isn't orderable reduce amount of bread in weekly basket -1

## views needed for the packing and ordering process:
 All overviews need to have a present and past version.
#### Overview of past orderings per shareholder: 

#### Overview of each depot:

#### View total orders of all depots:

#### View total bread order with preferences per depot:

#### View of modular products:
	e.g. hearbs, quark, extra vegetables (cheese)...

## Comments regarding the interface:


#### We need the following administration layers.
- Fulladmins
- Depotadmins (push to other depot function with notification to other depotadmin?) Access to depot overview, able to change momentary (and last week or all?) orderings)
- Oderingadmins (aces to all overviews, Products aces, weekly basket change, full past ordering aces)
- Userlevel (change momentary and regular ordering, view last orders)

